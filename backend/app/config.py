import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "The Lenny Growth Assistant"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Database Settings
    # Supports PostgreSQL (Supabase / Railway / Docker) or falls back to local SQLite
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'data' / 'lenny_assistant.db'}")
    
    # LLM Settings
    DEFAULT_PROVIDER: str = os.getenv("DEFAULT_PROVIDER", "ollama")  # 'ollama', 'anthropic', 'openai'
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.2")
    
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")
    
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o")
    
    # Transcripts & Knowledge Base
    TRANSCRIPTS_DIR: Path = BASE_DIR / "data" / "transcripts"
    CACHE_DIR: Path = BASE_DIR / "data"
    
    # CORS
    ALLOWED_ORIGINS: list[str] = ["*"]

    model_config = SettingsConfigDict(env_file=".env", extra="allow")

settings = Settings()
