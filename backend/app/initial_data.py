import asyncio
import logging
from sqlmodel import select
from app.core.database import async_session_maker
from app.models.artwork import User
from app.core.config import settings  # Tus settings globales con Pydantic
# Asumiendo que usas passlib para hashear contraseñas:
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
logger = logging.getLogger(__name__)

async def create_initial_admin() -> None:
    async with async_session_maker() as session:
        # Credenciales obtenidas de variables de entorno de forma segura
        admin_email = settings.FIRST_SUPERUSER_EMAIL
        admin_password = settings.FIRST_SUPERUSER_PASSWORD

        result = await session.execute(select(User).where(User.email == admin_email))
        existing_user = result.scalars().first()

        if not existing_user:
            hashed_password = pwd_context.hash(admin_password)
            user_in = User(
                email=admin_email,
                hashed_password=hashed_password,
                is_active=True
            )
            session.add(user_in)
            await session.commit()
            logger.info(f"✅ Superusuario inicial creado correctamente: {admin_email}")
        else:
            logger.info(f"ℹ️️ El superusuario {admin_email} ya existe en la base de datos.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(create_initial_admin())