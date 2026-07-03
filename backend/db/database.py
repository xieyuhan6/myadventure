from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.exc import ArgumentError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from core.config import settings

def _normalize_database_url(raw_url: str) -> str:
    value = (raw_url or "").strip()
    if value.startswith(("'", '"')) and value.endswith(("'", '"')):
        value = value[1:-1].strip()
    return value


def _fallback_database_url() -> str:
    return "sqlite:////tmp/database.db"


def _build_engine(database_url: str):
    engine_kwargs = {}
    if database_url.startswith("sqlite"):
        engine_kwargs["connect_args"] = {"check_same_thread": False}
    return create_engine(database_url, **engine_kwargs)


database_url = _normalize_database_url(settings.DATABASE_URL)

try:
    make_url(database_url)
except (ArgumentError, Exception):
    database_url = _fallback_database_url()

engine = _build_engine(database_url)

SessionLocal=sessionmaker(autocommit=False,autoflush=False,bind=engine)
Base=declarative_base()
def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()
def create_tables():
    Base.metadata.create_all(bind=engine)