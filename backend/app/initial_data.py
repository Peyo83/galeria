import asyncio
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

# Asegúrate de importar tu sesión de base de datos y tus modelos reales
from app.core.database import async_session_maker
from app.models.user import User  # Ajusta la ruta a tu modelo de usuario real
from app.core.security import get_password_hash  # Tu función de hasheo con passlib/bcrypt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_initial_admin(db: AsyncSession) -> None:
    # Define tus credenciales iniciales (pueden venir de config/env o hardcodeadas para el bootstrap local)
    admin_email = "admin@galeria.com"
    admin_password = "galeria_super_secure_admin_password_2026"
    
    # Comprobar si ya existe el usuario admin
    result = await db.execute(select(User).where(User.email == admin_email))
    existing_user = result.scalars().first()
    
    if not existing_user:
        user_in = User(
            email=admin_email,
            hashed_password=get_password_hash(admin_password),
            is_active=True,
            is_superuser=True
        )
        db.add(user_in)
        await db.commit()
        logger.info(f"✅ Usuario administrador creado exitosamente: {admin_email}")
    else:
        logger.info(f"ℹ️ El usuario administrador {admin_email} ya existe en la base de datos.")

async def init() -> None:
    async with async_session_maker() as session:
        await create_initial_admin(session)

if __name__ == "__main__":
    asyncio.run(init())