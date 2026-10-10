import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

logger = logging.getLogger(__name__)

Base = declarative_base()

def get_engine():
    db_url = settings.DATABASE_URL
    try:
        if db_url.startswith("postgresql"):
            # Attempt to connect to PostgreSQL with short timeout to detect offline DB
            logger.info(f"Attempting PostgreSQL connection: {db_url.split('@')[-1] if '@' in db_url else 'configured'}")
            engine = create_engine(db_url, connect_args={"connect_timeout": 3}, pool_pre_ping=True)
            # Test connection
            with engine.connect() as conn:
                pass
            logger.info("Successfully connected to PostgreSQL database.")
            return engine
    except Exception as e:
        logger.warning(f"PostgreSQL connection failed ({e}). Falling back to local persistent SQLite.")
    
    # Fallback SQLite
    sqlite_url = f"sqlite:///{settings.CACHE_DIR / 'lenny_assistant.db'}"
    logger.info(f"Using SQLite database: {sqlite_url}")
    return create_engine(sqlite_url, connect_args={"check_same_thread": False})

engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    from app.models.schemas import SessionModel, MessageModel, ArtifactModel, CitationModel  # noqa
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized with schema tables.")
