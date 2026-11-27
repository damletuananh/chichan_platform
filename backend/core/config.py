from pathlib import Path

from dotenv import load_dotenv
from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Neo đường dẫn .env vào thư mục backend/ để chạy `uvicorn main:app` từ đâu cũng đúng
# (trước đây load_dotenv() đọc theo CWD — chạy từ repo root sẽ âm thầm dùng toàn bộ
# giá trị mặc định: DB localhost, SECRET_KEY mặc định, AI_API_KEY rỗng).
BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = ""
    TURSO_DATABASE_URL: str = ""
    TURSO_AUTH_TOKEN: str = ""

    @staticmethod
    def _normalize_turso_url(raw_url: str) -> str:
        raw = raw_url.strip()
        secure_default = not raw.startswith(("http://", "ws://"))
        stripped = raw
        for prefix in ("sqlite+tursohttp://", "libsql://", "wss://", "ws://", "https://", "http://"):
            if stripped.startswith(prefix):
                stripped = stripped[len(prefix):]
                break
        host_and_path, _, query = stripped.partition("?")
        host = host_and_path.rstrip("/")
        if not query:
            query = "secure=true" if secure_default else "secure=false"
        return f"sqlite+tursohttp://{host}?{query}"

    @property
    def resolved_database_url(self) -> str:
        """Chuẩn hóa URL kết nối Database theo thứ tự ưu tiên:
        1. DATABASE_URL (hỗ trợ postgresql+asyncpg://, sqlite+aiosqlite:///, sqlite+tursohttp://, libsql://)
        2. TURSO_DATABASE_URL (tự động chuyển sang sqlite+tursohttp://)
        3. Mặc định fallback về database/chichan.db cục bộ."""
        url = self.DATABASE_URL.strip()
        if url:
            if url.startswith(("libsql://", "sqlite+tursohttp://")):
                return self._normalize_turso_url(url)
            if url.startswith("sqlite+aiosqlite:///"):
                raw_path = url[len("sqlite+aiosqlite:///"):]
                if raw_path != ":memory:" and not Path(raw_path).is_absolute():
                    repo_root = BASE_DIR.parent
                    if raw_path.startswith("../"):
                        target_path = (BASE_DIR / raw_path).resolve()
                    else:
                        target_path = (repo_root / raw_path).resolve()
                    return f"sqlite+aiosqlite:///{target_path.as_posix()}"
            return url

        if self.TURSO_DATABASE_URL.strip():
            return self._normalize_turso_url(self.TURSO_DATABASE_URL)

        default_path = (BASE_DIR.parent / "database" / "chichan.db").resolve()
        return f"sqlite+aiosqlite:///{default_path.as_posix()}"

    # Security
    # Chấp nhận cả JWT_SECRET_KEY (tên cũ trong docs deploy Render) như một alias.
    SECRET_KEY: str = Field(
        default="your-super-secret-key-change-me-in-production",
        validation_alias=AliasChoices("SECRET_KEY", "JWT_SECRET_KEY"),
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    ALLOWED_ORIGINS: str = "*"

    # AI (Gemini)
    AI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-3.6-flash"

    # Email / SMTP (Quên mật khẩu & Thông báo)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = ""
    SMTP_FROM_NAME: str = "ChiChan Education"
    SMTP_TLS: bool = True
    FRONTEND_URL: str = "http://localhost:3000"
    PASSWORD_RESET_EXPIRE_MINUTES: int = 15

    # SQL logging của SQLAlchemy (bật qua ECHO=true khi cần debug, mặc định tắt)
    ECHO: bool = False

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

settings = Settings()


def validate_settings() -> list[tuple[str, str]]:
    """Kiểm tra cấu hình runtime khi khởi động.

    Trả về danh sách (mức_log, mô_tả_vấn_đề). Hiện CHỈ WARN — sau một chu kỳ deploy
    ổn định trên Render, chuyển các mục CRITICAL thành raise RuntimeError
    (fail-loud) theo kế hoạch refactor phase 3.
    """
    problems: list[tuple[str, str]] = []

    if settings.SECRET_KEY == "your-super-secret-key-change-me-in-production":
        problems.append((
            "critical",
            "SECRET_KEY đang dùng giá trị mặc định không an toàn — JWT có thể bị làm giả. "
            "Hãy đặt SECRET_KEY (hoặc tên cũ JWT_SECRET_KEY) trên môi trường deploy.",
        ))

    valid_schemes = ("postgresql+asyncpg://", "sqlite+aiosqlite://", "sqlite+tursohttp://")
    resolved_url = settings.resolved_database_url
    if not any(resolved_url.startswith(s) for s in valid_schemes):
        problems.append((
            "critical",
            "DATABASE_URL hoặc TURSO_DATABASE_URL phải dùng scheme hợp lệ (sqlite+aiosqlite://, sqlite+tursohttp://, libsql://, postgresql+asyncpg://) — "
            "scheme khác sẽ lỗi khi mở kết nối.",
        ))
    elif resolved_url.startswith("sqlite+tursohttp://") and not settings.TURSO_AUTH_TOKEN and "authToken=" not in resolved_url and "auth_token=" not in resolved_url:
        problems.append((
            "critical",
            "TURSO_AUTH_TOKEN chưa được đặt khi kết nối Turso Cloud — truy vấn tới Turso sẽ bị từ chối xác thực.",
        ))

    if not settings.AI_API_KEY:
        problems.append((
            "warning",
            "AI_API_KEY chưa đặt — các tính năng AI (roleplay, embedding) sẽ lỗi khi gọi.",
        ))

    if settings.ALLOWED_ORIGINS.strip() == "*":
        problems.append((
            "warning",
            "ALLOWED_ORIGINS='*' — CORS mở cho mọi origin và allow_credentials bị tắt. "
            "App hiện gọi API bằng header Bearer (không cookie cross-origin) nên vẫn chạy "
            "bình thường, nhưng cấu hình này sẽ chặn các thiết kế cookie HttpOnly trong "
            "tương lai. Hãy liệt kê domain production cụ thể.",
        ))

    return problems
