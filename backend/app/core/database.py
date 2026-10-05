'''
===============================================================================
[FICHA GLOBAL]: ENGINE Y SESIÓN ASÍNCRONA DE BASE DE DATOS
===============================================================================
• Propósito Principal: Inicializar el Engine de SQLAlchemy usando el driver asyncpg y
                       proveer un generador de sesiones asíncronas (AsyncSession) por request.
• Dependencias: postgres:15-alpine (Docker network), variables de entorno (.env).
• Volumen Creado: Pool de conexiones asíncronas no bloqueante.
===============================================================================
'''

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession
from app.core.config import settings

# Motor asíncrono optimizado para alta concurrencia sin bloqueo del bucle de eventos
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True  # Prueba la vitalidad de la conexión (SELECT 1) antes de cada checkout del pool
)

async_session_maker = sessionmaker(
    bind=engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency Provider asíncrono que inyecta la sesión transaccional en los controladores de FastAPI."""
    async with async_session_maker() as session:
        yield session