"""Database connection layer: engine, session factory, Base, and get_db()."""
from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

DATABASE_URL = settings.sqlalchemy_url
IS_SQLITE = DATABASE_URL.startswith("sqlite")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if IS_SQLITE else {},
    pool_pre_ping=True,
)

if IS_SQLITE:
    # SQLite ignores foreign keys unless asked, so ON DELETE CASCADE would silently do nothing.
    @event.listens_for(engine, "connect")
    def _fk_on(dbapi_conn, _):
        dbapi_conn.execute("PRAGMA foreign_keys=ON")

SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)
Base = declarative_base()


def get_db():
    """Give a route a session, and always close it afterwards."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
