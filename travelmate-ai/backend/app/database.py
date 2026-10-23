from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import BACKEND_DIR, settings


def _resolve_url(url: str) -> str:
    """Anchor relative sqlite paths to the backend folder."""
    prefix = "sqlite:///./"
    if url.startswith(prefix):
        return f"sqlite:///{(BACKEND_DIR / url[len(prefix):]).as_posix()}"
    return url


DATABASE_URL = _resolve_url(settings.database_url)
IS_SQLITE = DATABASE_URL.startswith("sqlite")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args={"check_same_thread": False} if IS_SQLITE else {},
    echo=False,
)

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
