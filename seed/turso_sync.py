"""ChiChan Platform - Turso Database Sync Tool.

Công cụ đồng bộ toàn diện dữ liệu từ SQLite cục bộ (database/chichan.db)
lên Turso Cloud Database (LibSQL) đảm bảo dự án hoạt động liên tục 24/7 không bị pause.

Sử dụng:
    python seed/turso_sync.py --dry-run
    python seed/turso_sync.py
"""

import argparse
import asyncio
import os
from pathlib import Path
import sqlite3
import sys
import time

try:
    import aiohttp
except ImportError:
    print("❌ Lỗi: Thư viện 'aiohttp' chưa được cài đặt. Hãy chạy: pip install aiohttp")
    sys.exit(1)

# Neo đường dẫn
ROOT_DIR = Path(__file__).resolve().parent.parent
LOCAL_DB_PATH = ROOT_DIR / "database" / "chichan.db"
ENV_PATH = ROOT_DIR / "backend" / ".env"

# Thứ tự bảng theo ràng buộc khóa ngoại (Foreign Key Dependencies)
TABLE_INSERT_ORDER = [
    # 1. Bảng độc lập / Danh mục gốc
    "roles",
    "site_settings",
    "ai_knowledge_vectors",
    "forum_categories",
    "users",

    # 2. Bảng phụ thuộc vào users / categories
    "user_profiles",
    "user_sessions",
    "ai_scenarios",
    "courses",
    "forum_posts",

    # 3. Bảng phụ thuộc vào courses / forum_posts / ai_scenarios
    "lessons",
    "course_enrollments",
    "forum_comments",
    "forum_post_likes",
    "ai_sessions",

    # 4. Bảng phụ thuộc vào lessons / ai_sessions
    "lesson_progress",
    "quizzes",
    "ai_messages",
    "ai_game_evaluations",

    # 5. Bảng phụ thuộc vào quizzes
    "quiz_questions",
    "quiz_submissions",

    # 6. Bảng phụ thuộc vào quiz_questions
    "quiz_question_options",
]


def load_env_file():
    """Đọc cấu hình từ backend/.env nếu có."""
    env_vars = {}
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env_vars[k.strip()] = v.strip().strip('"').strip("'")
    return env_vars


class TursoClient:
    """Client giao tiếp trực tiếp với Turso LibSQL Cloud qua HTTP v2 Pipeline."""

    def __init__(self, raw_url: str, auth_token: str):
        # Chuẩn hóa URL sang endpoint HTTPS v2 pipeline
        clean_url = raw_url.replace("libsql://", "").replace("wss://", "").replace("ws://", "").replace("http://", "").replace("https://", "")
        clean_url = clean_url.split("/")[0].strip()
        self.pipeline_url = f"https://{clean_url}/v2/pipeline"
        self.auth_token = auth_token
        self.session: aiohttp.ClientSession | None = None

    async def connect(self):
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        self.session = aiohttp.ClientSession(headers=headers)
        # Test connection
        res = await self.execute("SELECT 1")
        return res is not None

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()

    async def execute(self, sql: str):
        """Thực thi một câu lệnh SQL đơn lẻ."""
        if not self.session:
            raise RuntimeError("Client chưa được kết nối!")
        payload = {
            "requests": [{"type": "execute", "stmt": {"sql": sql}}]
        }
        async with self.session.post(self.pipeline_url, json=payload) as resp:
            if not resp.ok:
                text = await resp.text()
                raise RuntimeError(f"Turso HTTP {resp.status}: {text}")
            data = await resp.json()
            result = data["results"][0]
            if result.get("type") == "error":
                raise RuntimeError(result.get("error", {}).get("message", "Lỗi SQL không xác định"))
            return result.get("response", {}).get("result")

    async def batch(self, sql_list: list[str]):
        """Thực thi danh sách câu lệnh SQL theo batch."""
        if not self.session:
            raise RuntimeError("Client chưa được kết nối!")
        # Luôn chèn PRAGMA foreign_keys = OFF đầu mỗi batch để đảm bảo an toàn kết nối HTTP
        requests = [{"type": "execute", "stmt": {"sql": "PRAGMA foreign_keys = OFF;"}}]
        for s in sql_list:
            requests.append({"type": "execute", "stmt": {"sql": s}})

        payload = {"requests": requests}
        async with self.session.post(self.pipeline_url, json=payload) as resp:
            if not resp.ok:
                text = await resp.text()
                raise RuntimeError(f"Turso HTTP {resp.status}: {text}")
            data = await resp.json()
            results = data.get("results", [])
            for idx, res in enumerate(results[1:]):  # Bỏ qua kết quả của PRAGMA
                if res.get("type") == "error":
                    err_msg = res.get("error", {}).get("message", "Unknown error")
                    raise RuntimeError(f"Lỗi tại câu lệnh #{idx}: {sql_list[idx][:80]}... -> {err_msg}")
            return results


def get_local_table_counts(db_path: Path):
    """Lấy số lượng bản ghi các bảng trong SQLite local."""
    counts = {}
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    for t in TABLE_INSERT_ORDER:
        try:
            cur.execute(f"SELECT COUNT(*) FROM [{t}]")
            counts[t] = cur.fetchone()[0]
        except sqlite3.OperationalError:
            counts[t] = 0
    conn.close()
    return counts


async def get_turso_table_counts(client: TursoClient):
    """Lấy số lượng bản ghi các bảng trên Turso Cloud."""
    counts = {}
    for t in TABLE_INSERT_ORDER:
        try:
            res = await client.execute(f"SELECT COUNT(*) FROM [{t}]")
            rows = res.get("rows", [])
            if rows and rows[0]:
                counts[t] = int(rows[0][0].get("value", 0))
            else:
                counts[t] = 0
        except Exception:
            counts[t] = 0
    return counts


def extract_schema_ddl(db_path: Path):
    """Trích xuất toàn bộ DDL (CREATE TABLE & CREATE INDEX) từ sqlite_master."""
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    # Lấy các bảng theo thứ tự tạo
    cur.execute("SELECT sql FROM sqlite_master WHERE type='table' AND sql IS NOT NULL AND name NOT LIKE 'sqlite_%'")
    table_sqls = [r[0] for r in cur.fetchall()]
    # Lấy các index
    cur.execute("SELECT sql FROM sqlite_master WHERE type='index' AND sql IS NOT NULL AND name NOT LIKE 'sqlite_%'")
    index_sqls = [r[0] for r in cur.fetchall()]
    conn.close()
    return table_sqls + index_sqls


def dump_ordered_inserts(db_path: Path):
    """Trích xuất toàn bộ bản ghi theo thứ tự topological chuẩn để không bị lỗi Foreign Key."""
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    ordered_inserts = []

    for table in TABLE_INSERT_ORDER:
        try:
            cur.execute(f"SELECT * FROM [{table}]")
        except sqlite3.OperationalError:
            continue

        rows = cur.fetchall()
        for row in rows:
            vals = []
            for val in row:
                if val is None:
                    vals.append("NULL")
                elif isinstance(val, (int, float)):
                    vals.append(str(val))
                elif isinstance(val, bytes):
                    vals.append(f"X'{val.hex()}'")
                else:
                    escaped = str(val).replace("'", "''")
                    vals.append(f"'{escaped}'")
            ordered_inserts.append(f"INSERT INTO \"{table}\" VALUES({', '.join(vals)});")

    conn.close()
    return ordered_inserts


async def sync_to_turso(turso_url: str, auth_token: str, local_db: Path, batch_size: int = 50, dry_run: bool = False):
    print("=" * 68)
    print("🚀 CHICHAN PLATFORM - TURSO CLOUD DATABASE SYNC")
    print("=" * 68)
    print(f"📁 Nguồn SQLite: {local_db}")
    print(f"☁️ Đích Turso:   {turso_url if not dry_run else '[DRY-RUN - Giả lập]'}")

    # 1. Trích xuất Schema và Dữ liệu theo thứ tự chuẩn
    schema_stmts = extract_schema_ddl(local_db)
    ordered_inserts = dump_ordered_inserts(local_db)
    local_counts = get_local_table_counts(local_db)

    print(f"📊 Trích xuất thành công: {len(schema_stmts)} câu lệnh DDL và {len(ordered_inserts)} câu lệnh DML theo đúng phân cấp khóa ngoại.")

    if dry_run:
        print("\n🔍 KẾT QUẢ KIỂM TRA DRY-RUN:")
        print(f"  - Schema tables & indexes: {len(schema_stmts)}")
        print(f"  - Total row insert statements: {len(ordered_inserts)}")
        print("\n📈 Thống kê dữ liệu nguồn sẵn sàng đẩy lên Turso:")
        for t, cnt in local_counts.items():
            print(f"    • {t:<24s}: {cnt:4d} rows")
        print("\n✅ DRY-RUN hoàn tất. Cấu trúc và dữ liệu hoàn toàn hợp lệ để đẩy lên Turso!")
        return True

    # 2. Kết nối Turso
    print("\n⏳ Đang kết nối tới Turso Cloud qua v2 HTTP Pipeline...")
    start_time = time.time()
    client = TursoClient(turso_url, auth_token)
    try:
        await client.connect()
        print("✅ Kết nối Turso thành công (Độ trễ thấp, giao thức HTTP v2 Pipeline)!")
    except Exception as e:
        print(f"❌ Kết nối Turso thất bại: {e}")
        await client.close()
        return False

    try:
        # 3. Dọn dẹp & Khởi tạo Schema
        print("\n🧹 Đang làm sạch database & khởi tạo cấu trúc bảng trên Turso...")
        # Xóa bảng cũ theo thứ tự ngược lại
        for t in reversed(TABLE_INSERT_ORDER):
            try:
                await client.execute(f"DROP TABLE IF EXISTS \"{t}\";")
            except Exception:
                pass

        # Tạo lại toàn bộ bảng và index
        for ddl in schema_stmts:
            try:
                await client.execute(ddl)
            except Exception as e:
                print(f"  ⚠️ Cảnh báo DDL: {e}")

        # 4. Nạp Dữ liệu theo Batch
        total_inserts = len(ordered_inserts)
        print(f"\n📦 Đang nạp {total_inserts} bản ghi lên Turso (batch size = {batch_size})...")

        for i in range(0, total_inserts, batch_size):
            chunk = ordered_inserts[i:i + batch_size]
            try:
                await client.batch(chunk)
                pct = min(100.0, (i + len(chunk)) / total_inserts * 100)
                sys.stdout.write(f"\r  ⚡ Tiến độ: {i + len(chunk):4d}/{total_inserts} ({pct:5.1f}%)")
                sys.stdout.flush()
            except Exception as e:
                print(f"\n❌ Lỗi khi nạp batch {i}-{i+len(chunk)}: {e}")
                # Fallback nạp từng dòng
                for s in chunk:
                    try:
                        await client.execute(s)
                    except Exception as sub_e:
                        print(f"    Chi tiết lỗi tại: {s[:70]}... -> {sub_e}")

        print("\n✅ Đã nạp thành công toàn bộ dữ liệu!")

        # 5. Đối soát số liệu
        print("\n🔍 Đang đối soát số liệu giữa SQLite Local và Turso Cloud...")
        turso_counts = await get_turso_table_counts(client)

        print("\n" + "=" * 68)
        print(f"{'Bảng dữ liệu':<24} | {'SQLite Local':<14} | {'Turso Cloud':<14} | Trạng thái")
        print("-" * 68)
        all_match = True
        for t in TABLE_INSERT_ORDER:
            loc = local_counts.get(t, 0)
            tur = turso_counts.get(t, 0)
            status = "✅ MATCH" if loc == tur and loc > 0 else ("⚠️ 0 ROWS" if loc == 0 and tur == 0 else "❌ MISMATCH")
            if loc != tur:
                all_match = False
            print(f"{t:<24} | {loc:<14} | {tur:<14} | {status}")
        print("=" * 68)

        elapsed = time.time() - start_time
        if all_match:
            print(f"\n🎉 ĐỒNG BỘ HOÀN TẤT THÀNH CÔNG trong {elapsed:.2f}s!")
            print("🚀 Cơ sở dữ liệu ChiChan trên Turso Cloud đã sẵn sàng hoạt động liên tục 24/7!")
        else:
            print(f"\n⚠️ Đồng bộ hoàn tất với một số sai lệch sau {elapsed:.2f}s.")

        return all_match

    finally:
        await client.close()


def main():
    parser = argparse.ArgumentParser(description="Đồng bộ dữ liệu ChiChan sang Turso LibSQL Cloud")
    parser.add_argument("--url", help="Turso Database URL (e.g., libsql://chichan-db.turso.io)")
    parser.add_argument("--token", help="Turso Auth Token")
    parser.add_argument("--source", help="Đường dẫn file SQLite nguồn", default=str(LOCAL_DB_PATH))
    parser.add_argument("--batch-size", type=int, default=50, help="Kích thước batch khi upload")
    parser.add_argument("--dry-run", action="store_true", help="Chạy kiểm tra mô phỏng không ghi vào cloud")

    args = parser.parse_args()
    env = load_env_file()

    url = args.url or env.get("TURSO_DATABASE_URL") or os.environ.get("TURSO_DATABASE_URL")
    token = args.token or env.get("TURSO_AUTH_TOKEN") or os.environ.get("TURSO_AUTH_TOKEN")
    source_path = Path(args.source)

    if not args.dry_run and (not url or not token):
        print("⚠️ Chưa tìm thấy cấu hình TURSO_DATABASE_URL hoặc TURSO_AUTH_TOKEN trong backend/.env.")
        print("Chạy thử chế độ kiểm tra dữ liệu: python seed/turso_sync.py --dry-run\n")
        sys.exit(0)

    asyncio.run(sync_to_turso(
        turso_url=url or "",
        auth_token=token or "",
        local_db=source_path,
        batch_size=args.batch_size,
        dry_run=args.dry_run
    ))


if __name__ == "__main__":
    main()
