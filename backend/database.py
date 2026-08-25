import os
import urllib.parse
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Load environment variables from .env file
load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "smart_parking_db")

# URL-encode password in case it contains special characters
encoded_password = urllib.parse.quote_plus(DB_PASSWORD)

# MySQL Connection String using PyMySQL
DATABASE_URL = os.getenv("DATABASE_URL") or f"mysql+pymysql://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"

# Engine configuration supporting both MySQL and SQLite
engine_kwargs = {"echo": False}
if "sqlite" in DATABASE_URL:
    from sqlalchemy.pool import StaticPool
    engine_kwargs["connect_args"] = {"check_same_thread": False}
    engine_kwargs["poolclass"] = StaticPool
else:
    engine_kwargs.update({
        "pool_pre_ping": True,
        "pool_recycle": 3600,
        "pool_size": 10,
        "max_overflow": 20
    })

engine = create_engine(DATABASE_URL, **engine_kwargs)


# SessionLocal class for creating database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative Base for ORM models
Base = declarative_base()


def get_db():
    """
    FastAPI dependency that provides a transactional database session
    and ensures it is closed after request processing.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
