from pydantic import computed_field, ConfigDict
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        extra="ignore"
    )

    PROJECT_NAME: str
    VERSION: str
    API_V1_STR: str

    # Infraestructura PostgreSQL
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: int
    
    # Autenticación JWT Admin
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # ── Credenciales del Superusuario inicial (leídas del .env) ──
    FIRST_SUPERUSER_EMAIL: str
    FIRST_SUPERUSER_PASSWORD: str

    # Network & Security (CORS)
    CORS_ORIGINS: List[str]

    model_config = ConfigDict(env_file=".env", extra="ignore")

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        """DSN asíncrono hacia el contenedor galeria_db en la red interna de Docker."""
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@galeria_db:5432/{self.POSTGRES_DB}"

settings = Settings()