# backend/app/core/database.py
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession
from app.core.config import settings

# Motor asíncrono configurado para lidiar con altas cargas I/O sin bloquear hilos
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True
)

async_session_maker = sessionmaker(
    bind=engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

async def get_db() -> AsyncSession:
    """Dependency Provider para inyectar la sesión asíncrona en los endpoints."""
    async with async_session_maker() as session:
        yield session