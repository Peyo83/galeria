# backend/app/core/config.py
from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        extra="ignore"
    )

    PROJECT_NAME: str = "Galería de Arte API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Inyección de Infraestructura
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: int
    
    # Proveedor de LLM para LangChain
    OPENAI_API_KEY: str

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        """Construye dinámicamente el DSN asíncrono para asyncpg apuntando a la red Docker internamente."""
        # Se asume 'galeria_db' como el service name/host definido en la red interna de Docker[cite: 3]
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@galeria_db:5432/{self.POSTGRES_DB}"

settings = Settings()