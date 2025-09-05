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
    # DB_DIR: Path = PROJECT_ROOT / "data"
    # TENANT_DB_FILE: Path = DB_DIR / "engrammer_tenants.db"

    DATABASE_URL: str = f"sqlite:///{(PROJECT_ROOT / 'data' / 'engrammer.db').as_posix()}"
    
    SQLALCHEMY_ECHO: bool = False 
    
    NEO4J_IMAGE: str = "neo4j"   
    DOCKER_NETWORK: str = "engrammer_net"     
    NEO4J_WITH_APOC: bool = True
    
    #Keycloack
    KEYCLOAK_SERVER_URL: str | None = None
    KEYCLOAK_REALM: str | None = None
    KEYCLOAK_CLIENT_ID: str | None = None
    KEYCLOAK_AUDIENCE: str | None = None
    KEYCLOAK_CLIENT_SECRET: str | None = None      
    
    @property
    def KEYCLOAK_ISSUER(self) -> str | None:
        if not self.KEYCLOAK_SERVER_URL or not self.KEYCLOAK_REALM:
            return None
        base = self.KEYCLOAK_SERVER_URL.rstrip("/")
        return f"{base}/realms/{self.KEYCLOAK_REALM}"

    @property
    def KEYCLOAK_JWKS_URL(self) -> str | None:
        iss = self.KEYCLOAK_ISSUER
        return f"{iss}/protocol/openid-connect/certs" if iss else None        
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
