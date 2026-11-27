from urllib.parse import urlsplit
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from core.config import settings
import core.turso_dialect  # noqa: F401 - Đăng ký dialect sqlite+tursohttp cho SQLAlchemy

db_url = settings.resolved_database_url if hasattr(settings, "resolved_database_url") else settings.DATABASE_URL
is_turso = db_url.startswith("sqlite+tursohttp://")
is_sqlite = db_url.startswith("sqlite")

# Log chẩn đoán loại DB (ẩn toàn bộ credential/token)
_parsed = urlsplit(db_url)
print(f"[DB] Dialect={_parsed.scheme} Host={_parsed.hostname or 'local'}")

# Khởi tạo Async Engine cho SQLAlchemy (echo điều khiển qua biến ECHO trong .env)
if is_turso:
    connect_args = {}
    if getattr(settings, "TURSO_AUTH_TOKEN", None):
        connect_args["auth_token"] = settings.TURSO_AUTH_TOKEN
    engine = create_async_engine(
        db_url,
        echo=settings.ECHO,
        future=True,
        pool_size=5,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=300,
        connect_args=connect_args
    )
elif is_sqlite:
    engine = create_async_engine(
        db_url,
        echo=settings.ECHO,
        future=True,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_async_engine(
        db_url,
        echo=settings.ECHO,
        future=True,
        # Cấu hình pool tường minh cho PostgreSQL
        pool_size=10,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=300,
        pool_pre_ping=True,
        connect_args={"statement_cache_size": 0}
    )

# Khởi tạo Async Session Maker
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base class cho tất cả các model ORM
Base = declarative_base()

# Dependency để lấy database session
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
