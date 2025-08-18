from functools import lru_cache
from pydantic_settings import BaseSettings
from typing import List
from dotenv import load_dotenv
from pathlib import Path


load_dotenv(".env")

class Settings(BaseSettings):
    ENV: str = "dev"

    # Server
    API_V1_PREFIX: str = "/v1"
    CORS_ALLOW_ORIGINS: List[str] = ["*"]

    OPENAI_API_KEY: str | None = None
    OLLAMA_HOST: str | None = None

    # Logging
    LOG_LEVEL: str = "INFO"
    
    #Persistence
    PROJECT_ROOT: Path = Path(__file__).resolve().parents[2]
    DB_DIR: Path = PROJECT_ROOT / "data"
    DB_FILE: Path = DB_DIR / "engrammer.db"

    DATABASE_URL: str = f"sqlite:///{(PROJECT_ROOT / 'data' / 'engrammer.db').as_posix()}"
    SQLALCHEMY_ECHO: bool = False 
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
