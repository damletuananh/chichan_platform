"""SQLAlchemy 2.0 Async Dialect cho Turso LibSQL Cloud qua HTTP v2 Pipeline (/v2/pipeline).

Hỗ trợ đầy đủ `create_async_engine("sqlite+tursohttp://...")` trên cả Windows và Linux
mà không cần biên dịch thư viện native (Rust/C++ MSVC), giao tiếp qua HTTPS `httpx`.
"""

from __future__ import annotations

import base64
from collections import deque
import math
import sqlite3
from typing import Any, Deque, Iterator, NoReturn, Optional, Sequence
import urllib.parse

import httpx
from sqlalchemy import pool
from sqlalchemy.connectors.asyncio import AsyncAdapt_dbapi_module
from sqlalchemy.dialects import registry
from sqlalchemy.dialects.sqlite.aiosqlite import SQLiteDialect_aiosqlite
from sqlalchemy.engine import AdaptedConnection
from sqlalchemy.engine.interfaces import DBAPIConnection, IsolationLevel
from sqlalchemy.engine.url import URL
from sqlalchemy.util.concurrency import await_fallback, await_only


def _encode_arg(value: Any) -> dict[str, Any]:
    """Chuyển đổi tham số Python sang kiểu giá trị Hrana JSON v2 của Turso."""
    if value is None:
        return {"type": "null"}
    if isinstance(value, bool):
        return {"type": "integer", "value": "1" if value else "0"}
    if isinstance(value, int):
        return {"type": "integer", "value": str(value)}
    if isinstance(value, float):
        if not math.isfinite(value):
            return {"type": "null"}
        return {"type": "float", "value": value}
    if isinstance(value, (bytes, bytearray, memoryview)):
        return {
            "type": "blob",
            "base64": base64.b64encode(bytes(value)).decode("ascii"),
        }
    return {"type": "text", "value": str(value)}


def _decode_cell(cell: dict[str, Any]) -> Any:
    """Giải mã một ô kết quả từ phản hồi JSON v2 của Turso về kiểu Python."""
    ctype = cell.get("type")
    if ctype == "null" or ctype is None:
        return None
    if ctype == "integer":
        return int(cell["value"])
    if ctype == "float":
        return float(cell["value"])
    if ctype == "text":
        return cell["value"]
    if ctype == "blob":
        b64 = cell["base64"]
        padding = "=" * (-len(b64) % 4)
        return base64.b64decode(b64 + padding)
    return cell.get("value")


def _map_turso_error(message: str, code: str = "") -> Exception:
    """Ánh xạ mã lỗi SQL từ Turso sang đúng lớp Exception PEP 249 / sqlite3
    để SQLAlchemy nhận diện IntegrityError / OperationalError chính xác."""
    lower = message.lower()
    if (
        "constraint failed" in lower
        or "unique" in lower
        or "foreign key" in lower
        or "sqlite_constraint" in code.lower()
    ):
        return sqlite3.IntegrityError(message)
    if "syntax error" in lower or "no such" in lower:
        return sqlite3.OperationalError(message)
    return sqlite3.OperationalError(f"{code}: {message}" if code else message)


class _AsyncTursoHttpCursor:
    """Cursor bất đồng bộ giao tiếp qua AsyncTursoHttpConnection."""

    def __init__(self, conn: AsyncTursoHttpConnection) -> None:
        self._conn = conn
        self.description: Optional[tuple[tuple[Any, ...], ...]] = None
        self.rowcount: int = -1
        self.lastrowid: Optional[int] = None
        self._rows: list[tuple[Any, ...]] = []

    async def execute(self, operation: str, parameters: Optional[Sequence[Any]] = None) -> None:
        cols, rows, rowcount, lastrowid = await self._conn._execute(operation, parameters)
        if cols:
            self.description = tuple((c["name"], None, None, None, None, None, None) for c in cols)
            self._rows = rows
            self.rowcount = -1
            self.lastrowid = lastrowid
        else:
            self.description = None
            self._rows = []
            self.rowcount = rowcount
            self.lastrowid = lastrowid

    async def executemany(
        self,
        operation: str,
        seq_of_parameters: Sequence[Sequence[Any]],
    ) -> None:
        rowcount, lastrowid = await self._conn._executemany(operation, seq_of_parameters)
        self.description = None
        self._rows = []
        self.rowcount = rowcount
        self.lastrowid = lastrowid

    async def fetchall(self) -> list[tuple[Any, ...]]:
        rows = self._rows
        self._rows = []
        return rows

    async def close(self) -> None:
        self._rows = []


class AsyncTursoHttpConnection:
    """Kết nối bất đồng bộ quản lý phiên Hrana HTTP v2 (`baton` trong transaction)."""

    def __init__(self, pipeline_url: str, auth_token: str = "", timeout: float = 30.0) -> None:
        self._root_url = pipeline_url
        self._active_url = pipeline_url
        self._auth_token = auth_token
        self._timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None
        self.isolation_level: Optional[str] = ""
        self._baton: Optional[str] = None
        self._in_tx: bool = False
        self._want_begin: bool = False

    def _ensure_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            headers = {"Content-Type": "application/json"}
            if self._auth_token:
                headers["Authorization"] = f"Bearer {self._auth_token}"
            self._client = httpx.AsyncClient(headers=headers, timeout=self._timeout)
        return self._client

    def begin(self) -> None:
        """Đánh dấu trì hoãn BEGIN để gộp chung vào HTTP request đầu tiên của giao dịch."""
        if self.isolation_level is not None and not self._in_tx:
            self._want_begin = True

    def _reset_stream(self) -> None:
        self._baton = None
        self._active_url = self._root_url
        self._in_tx = False
        self._want_begin = False

    async def _post_pipeline(self, requests: list[dict[str, Any]]) -> dict[str, Any]:
        client = self._ensure_client()
        payload: dict[str, Any] = {"requests": requests}
        if self._baton:
            payload["baton"] = self._baton

        resp = await client.post(self._active_url, json=payload)

        # Nếu baton idle quá lâu trên server (khi chưa mở transaction thực), mở lại stream mới sạch
        if not resp.is_success and self._baton and not self._in_tx:
            self._reset_stream()
            payload.pop("baton", None)
            resp = await client.post(self._active_url, json=payload)

        if not resp.is_success:
            raise sqlite3.OperationalError(f"Turso HTTP {resp.status_code}: {resp.text[:300]}")

        data = resp.json()
        self._baton = data.get("baton")
        base_url = data.get("base_url")
        if self._baton and base_url:
            self._active_url = base_url.rstrip("/") + "/v2/pipeline"
        elif not self._baton:
            self._active_url = self._root_url
        return data

    def _build_stmt(self, sql: str, parameters: Optional[Sequence[Any]]) -> dict[str, Any]:
        stmt: dict[str, Any] = {"sql": sql}
        if parameters:
            stmt["args"] = [_encode_arg(v) for v in parameters]
        return {"type": "execute", "stmt": stmt}

    async def _execute(
        self,
        sql: str,
        parameters: Optional[Sequence[Any]] = None,
    ) -> tuple[list[dict[str, Any]], list[tuple[Any, ...]], int, Optional[int]]:
        sql_stripped = sql.lstrip()
        sql_upper = sql_stripped[:16].upper()
        requests: list[dict[str, Any]] = []

        # Luôn bật foreign_keys khi mở stream mới để ON DELETE CASCADE hoạt động chuẩn
        if self._baton is None:
            requests.append({"type": "execute", "stmt": {"sql": "PRAGMA foreign_keys = ON;"}})

        if self._want_begin and not sql_upper.startswith(("BEGIN", "COMMIT", "ROLLBACK", "PRAGMA")):
            requests.append({"type": "execute", "stmt": {"sql": "BEGIN"}})
            self._want_begin = False
            self._in_tx = True

        target_idx = len(requests)
        requests.append(self._build_stmt(sql, parameters))

        # Truy vấn đơn lẻ ngoài transaction: đóng stream ngay trong cùng request để không giữ state
        auto_close = (not self._in_tx) and (not self._want_begin) and not sql_upper.startswith("BEGIN")
        if auto_close:
            requests.append({"type": "close"})

        data = await self._post_pipeline(requests)
        results = data.get("results", [])

        for res in results:
            if res.get("type") == "error":
                err = res.get("error", {})
                raise _map_turso_error(err.get("message", "Unknown Turso SQL error"), err.get("code", ""))

        if sql_upper.startswith("BEGIN"):
            self._in_tx = True
            self._want_begin = False
        elif auto_close:
            self._baton = None
            self._active_url = self._root_url

        exec_res = results[target_idx]["response"]["result"]
        cols = exec_res.get("cols") or []
        raw_rows = exec_res.get("rows") or []
        rows = [tuple(_decode_cell(cell) for cell in row) for row in raw_rows]
        rowcount = int(exec_res.get("affected_row_count") or 0)
        raw_last_id = exec_res.get("last_insert_rowid")
        lastrowid = int(raw_last_id) if raw_last_id is not None else None
        return cols, rows, rowcount, lastrowid

    async def _executemany(
        self,
        sql: str,
        seq_of_parameters: Sequence[Sequence[Any]],
    ) -> tuple[int, Optional[int]]:
        params_list = list(seq_of_parameters)
        if not params_list:
            return 0, None

        requests: list[dict[str, Any]] = []
        if self._baton is None:
            requests.append({"type": "execute", "stmt": {"sql": "PRAGMA foreign_keys = ON;"}})

        if self._want_begin:
            requests.append({"type": "execute", "stmt": {"sql": "BEGIN"}})
            self._want_begin = False
            self._in_tx = True

        stmt_start = len(requests)
        for p in params_list:
            requests.append(self._build_stmt(sql, p))
        stmt_end = len(requests)

        auto_close = (not self._in_tx) and (not self._want_begin)
        if auto_close:
            requests.append({"type": "close"})

        data = await self._post_pipeline(requests)
        results = data.get("results", [])
        for res in results:
            if res.get("type") == "error":
                err = res.get("error", {})
                raise _map_turso_error(err.get("message", "Unknown Turso SQL error"), err.get("code", ""))

        if auto_close:
            self._baton = None
            self._active_url = self._root_url

        total_rows = 0
        last_id: Optional[int] = None
        for res in results[stmt_start:stmt_end]:
            r = res["response"]["result"]
            total_rows += int(r.get("affected_row_count") or 0)
            if r.get("last_insert_rowid") is not None:
                last_id = int(r["last_insert_rowid"])
        return total_rows, last_id

    async def cursor(self) -> _AsyncTursoHttpCursor:
        return _AsyncTursoHttpCursor(self)

    async def execute(self, sql: str, parameters: Optional[Sequence[Any]] = None) -> _AsyncTursoHttpCursor:
        cur = await self.cursor()
        await cur.execute(sql, parameters)
        return cur

    async def commit(self) -> None:
        if self._in_tx and self._baton:
            try:
                data = await self._post_pipeline([
                    {"type": "execute", "stmt": {"sql": "COMMIT"}},
                    {"type": "close"},
                ])
                for res in data.get("results", []):
                    if res.get("type") == "error":
                        err = res.get("error", {})
                        raise _map_turso_error(err.get("message", "COMMIT failed"), err.get("code", ""))
            finally:
                self._reset_stream()
        else:
            self._reset_stream()

    async def rollback(self) -> None:
        if self._in_tx and self._baton:
            try:
                await self._post_pipeline([
                    {"type": "execute", "stmt": {"sql": "ROLLBACK"}},
                    {"type": "close"},
                ])
            except Exception:
                # Nếu baton đã hết hạn trên server thì giao dịch cũng đã tự động rollback
                pass
            finally:
                self._reset_stream()
        else:
            self._reset_stream()

    async def close(self) -> None:
        try:
            if self._baton and self._client and not self._client.is_closed:
                await self._client.post(
                    self._active_url,
                    json={"baton": self._baton, "requests": [{"type": "close"}]},
                )
        except Exception:
            pass
        finally:
            self._reset_stream()
            if self._client and not self._client.is_closed:
                await self._client.aclose()


class AsyncAdapt_tursohttp_cursor:
    """Adapter DBAPI cursor đồng bộ bề mặt cho greenlet SQLAlchemy AsyncEngine."""

    __slots__ = (
        "_adapt_connection",
        "_connection",
        "description",
        "await_",
        "_rows",
        "arraysize",
        "rowcount",
        "lastrowid",
    )

    def __init__(self, adapt_connection: AsyncAdapt_tursohttp_connection) -> None:
        self._adapt_connection = adapt_connection
        self._connection = adapt_connection._connection
        self.await_ = adapt_connection.await_
        self.arraysize = 1
        self.rowcount = -1
        self.lastrowid: Optional[int] = None
        self.description: Optional[tuple[tuple[Any, ...], ...]] = None
        self._rows: Deque[Any] = deque()

    async def _async_soft_close(self) -> None:
        return

    def close(self) -> None:
        self._rows.clear()

    def execute(self, operation: Any, parameters: Optional[Any] = None) -> Any:
        try:
            _cursor = self.await_(self._connection.cursor())
            self.await_(_cursor.execute(operation, parameters))
            if _cursor.description:
                self.description = _cursor.description
                self.lastrowid = _cursor.lastrowid if _cursor.lastrowid is not None else -1
                self.rowcount = -1
                self._rows = deque(self.await_(_cursor.fetchall()))
            else:
                self.description = None
                self.lastrowid = _cursor.lastrowid
                self.rowcount = _cursor.rowcount
            self.await_(_cursor.close())
        except Exception as error:
            self._adapt_connection._handle_exception(error)

    def executemany(self, operation: Any, seq_of_parameters: Any) -> Any:
        try:
            _cursor = self.await_(self._connection.cursor())
            self.await_(_cursor.executemany(operation, seq_of_parameters))
            self.description = None
            self.lastrowid = _cursor.lastrowid
            self.rowcount = _cursor.rowcount
            self.await_(_cursor.close())
        except Exception as error:
            self._adapt_connection._handle_exception(error)

    def setinputsizes(self, *inputsizes: Any) -> None:
        pass

    def __iter__(self) -> Iterator[Any]:
        while self._rows:
            yield self._rows.popleft()

    def fetchone(self) -> Optional[Any]:
        return self._rows.popleft() if self._rows else None

    def fetchmany(self, size: Optional[int] = None) -> Sequence[Any]:
        if size is None:
            size = self.arraysize
        return [self._rows.popleft() for _ in range(min(size, len(self._rows)))]

    def fetchall(self) -> Sequence[Any]:
        retval = list(self._rows)
        self._rows.clear()
        return retval


class AsyncAdapt_tursohttp_connection(AdaptedConnection):
    await_ = staticmethod(await_only)
    __slots__ = ("dbapi",)

    def __init__(self, dbapi: AsyncAdapt_tursohttp_dbapi, connection: AsyncTursoHttpConnection) -> None:
        self.dbapi = dbapi
        self._connection = connection

    @property
    def isolation_level(self) -> Optional[str]:
        return self._connection.isolation_level

    @isolation_level.setter
    def isolation_level(self, value: Optional[str]) -> None:
        self._connection.isolation_level = value

    def begin(self) -> None:
        self._connection.begin()

    def cursor(self, server_side: bool = False) -> AsyncAdapt_tursohttp_cursor:
        return AsyncAdapt_tursohttp_cursor(self)

    def execute(self, *args: Any, **kw: Any) -> Any:
        return self.await_(self._connection.execute(*args, **kw))

    def rollback(self) -> None:
        try:
            self.await_(self._connection.rollback())
        except Exception as error:
            self._handle_exception(error)

    def commit(self) -> None:
        try:
            self.await_(self._connection.commit())
        except Exception as error:
            self._handle_exception(error)

    def close(self) -> None:
        try:
            self.await_(self._connection.close())
        except Exception as error:
            self._handle_exception(error)

    def _handle_exception(self, error: Exception) -> NoReturn:
        raise error


class AsyncAdaptFallback_tursohttp_connection(AsyncAdapt_tursohttp_connection):
    __slots__ = ()
    await_ = staticmethod(await_fallback)


class AsyncAdapt_tursohttp_dbapi(AsyncAdapt_dbapi_module):
    """Module DBAPI giả lập chuẩn PEP 249 tương thích sqlite3 cho SQLAlchemy."""

    def __init__(self) -> None:
        self.paramstyle = "qmark"
        self.apilevel = "2.0"
        self.threadsafety = 1
        self.has_stop = False
        self.sqlite_version = "3.47.0"
        self.sqlite_version_info = (3, 47, 0)

        for name in (
            "Error",
            "InterfaceError",
            "DatabaseError",
            "DataError",
            "OperationalError",
            "IntegrityError",
            "InternalError",
            "ProgrammingError",
            "NotSupportedError",
            "Warning",
            "PARSE_COLNAMES",
            "PARSE_DECLTYPES",
            "Binary",
        ):
            setattr(self, name, getattr(sqlite3, name))

    def connect(
        self,
        pipeline_url: str,
        auth_token: str = "",
        timeout: float = 30.0,
        async_fallback: bool = False,
        **_: Any,
    ) -> AsyncAdapt_tursohttp_connection:
        conn = AsyncTursoHttpConnection(pipeline_url, auth_token=auth_token, timeout=timeout)
        if async_fallback:
            return AsyncAdaptFallback_tursohttp_connection(self, conn)
        return AsyncAdapt_tursohttp_connection(self, conn)


class SQLiteDialect_tursohttp(SQLiteDialect_aiosqlite):
    """SQLAlchemy asyncio dialect cho Turso Cloud HTTP v2 Pipeline (`sqlite+tursohttp://`)."""

    name = "sqlite"
    driver = "tursohttp"
    is_async = True
    has_terminate = False
    supports_statement_cache = True
    supports_server_side_cursors = False

    @classmethod
    def import_dbapi(cls) -> AsyncAdapt_tursohttp_dbapi:
        return AsyncAdapt_tursohttp_dbapi()

    def on_connect(self) -> None:
        # Turso HTTP không hỗ trợ sqlite3.create_function (REGEXP/floor UDFs)
        return None

    def get_isolation_level(self, dbapi_connection: DBAPIConnection) -> IsolationLevel:
        return "SERIALIZABLE"

    def set_isolation_level(
        self,
        dbapi_connection: DBAPIConnection,
        level: IsolationLevel,
    ) -> None:
        dbapi_connection.isolation_level = None if level == "AUTOCOMMIT" else ""

    def do_begin(self, dbapi_connection: DBAPIConnection) -> None:
        if hasattr(dbapi_connection, "begin"):
            dbapi_connection.begin()

    def create_connect_args(self, url: URL) -> tuple[list[Any], dict[str, Any]]:
        query = dict(url.query)
        secure_raw = str(query.pop("secure", "true")).lower()
        scheme = "http" if secure_raw in ("0", "false", "no") else "https"
        auth_token = query.pop("authToken", None) or query.pop("auth_token", "")
        timeout = float(query.pop("timeout", 30.0))

        host = url.host or ""
        if not host:
            # Hỗ trợ dạng tursohttp:///path.turso.io nếu thiếu slash
            host = (url.database or "").strip("/")
        netloc = f"{host}:{url.port}" if url.port else host
        pipeline_url = urllib.parse.urlunsplit((scheme, netloc, "/v2/pipeline", "", ""))

        opts: dict[str, Any] = {"timeout": timeout}
        if auth_token:
            opts["auth_token"] = auth_token
        return ([pipeline_url], opts)

    @classmethod
    def get_pool_class(cls, url: URL) -> type[pool.Pool]:
        return pool.AsyncAdaptedQueuePool


dialect = SQLiteDialect_tursohttp
registry.register("sqlite.tursohttp", "core.turso_dialect", "SQLiteDialect_tursohttp")
registry.register("tursohttp", "core.turso_dialect", "SQLiteDialect_tursohttp")
