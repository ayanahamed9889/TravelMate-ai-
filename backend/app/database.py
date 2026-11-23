import os

from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import BACKEND_DIR, settings


def _normalize_database_url(url: str) -> str:
    """Return a SQLAlchemy-compatible URL without logging credentials."""
    url = url.strip()
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    return url


def _resolve_url(url: str) -> str:
    """Anchor relative SQLite paths to the backend folder."""
    url = _normalize_database_url(url)
    prefix = "sqlite:///./"
    if url.startswith(prefix):
        return f"sqlite:///{(BACKEND_DIR / url[len(prefix):]).as_posix()}"
    return url


DATABASE_URL = _resolve_url(settings.database_url)
IS_SQLITE = DATABASE_URL.startswith("sqlite")
IS_POSTGRES = DATABASE_URL.startswith(("postgresql://", "postgresql+"))

# Vercel functions are read-only apart from /tmp. Fail clearly rather than silently
# accepting a local SQLite URL in a production environment.
if os.getenv("VERCEL") and not IS_POSTGRES:
    raise RuntimeError("VERCEL requires a PostgreSQL DATABASE_URL")

engine_options = {
    "pool_pre_ping": True,
    "echo": False,
}
if IS_SQLITE:
    engine_options["connect_args"] = {"check_same_thread": False}
else:
    engine_options["pool_recycle"] = 280

engine = create_engine(DATABASE_URL, **engine_options)

if IS_SQLITE:
    @event.listens_for(engine, "connect")
    def _enable_sqlite_fk(dbapi_conn, _record):
        # Make ON DELETE CASCADE actually work on SQLite
        cur = dbapi_conn.cursor()
        cur.execute("PRAGMA foreign_keys=ON")
        cur.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
