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

    # Infraestructura PostgreSQL
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: int  # Mapeado en Host, pero ignorado internamente para inter-conectividad
    
    # Credenciales del ecosistema de Inteligencia Artificial
    OPENAI_API_KEY: str
    GEMINI_API_KEY: str

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        """Construye dinámicamente el DSN asíncrono apuntando al puerto de la interfaz de red interna de Docker."""
        # Forzamos 5432 porque el backend se comunica directo en la subnet de Docker, no a través del puerto expuesto del Host.
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@galeria_db:5432/{self.POSTGRES_DB}"

settings = Settings()