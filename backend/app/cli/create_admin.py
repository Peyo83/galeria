import argparse
import asyncio
import getpass
import sys

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import async_session_maker
from app.core.security import get_password_hash
from app.models.artwork import User


async def create_admin_user(email: str, password: str) -> None:
    """Inyecta de forma idempotente el usuario Administrador en PostgreSQL."""
    async with async_session_maker() as session:  # type: AsyncSession
        try:
            # Check de existencia por email
            statement = select(User).where(User.email == email)
            result = await session.execute(statement)
            existing_user = result.scalar_one_or_none()

            if existing_user:
                print(f"[⚠️  WARN] El usuario '{email}' ya existe en la base de datos.")
                if not existing_user.is_active:
                    print("[🔄 UPDATE] Activando usuario previamente desactivado...")
                    existing_user.is_active = True
                    session.add(existing_user)
                    await session.commit()
                    print(f"[✅ OK] Usuario '{email}' reactivado correctamente.")
                return

            # Generar hash Bcrypt e insertar
            hashed_pw = get_password_hash(password)
            admin_user = User(
                email=email,
                hashed_password=hashed_pw,
                is_active=True,
            )

            session.add(admin_user)
            await session.commit()
            await session.refresh(admin_user)

            print(f"[✅ OK] Administrador creado exitosamente:")
            print(f"       - ID: {admin_user.id}")
            print(f"       - Email: {admin_user.email}")
            print(f"       - Active: {admin_user.is_active}")

        except Exception as e:
            await session.rollback()
            print(f"[❌ ERROR] Fallo al insertar usuario en la BBDD: {e}", file=sys.stderr)
            sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="CLI bootstrapping para usuario Admin del CMS.")
    parser.add_argument("--email", type=str, help="Email del administrador.")
    parser.add_argument("--password", type=str, help="Contraseña en plano.")

    args = parser.parse_args()

    email = args.email or input("Email admin: ").strip()
    if not email:
        print("[❌ ERROR] El email es obligatorio.", file=sys.stderr)
        sys.exit(1)

    password = args.password
    if not password:
        password = getpass.getpass("Contraseña: ")
        confirm_password = getpass.getpass("Confirmar contraseña: ")
        if password != confirm_password:
            print("[❌ ERROR] Las contraseñas no coinciden.", file=sys.stderr)
            sys.exit(1)

    if len(password) < 8:
        print("[❌ ERROR] La contraseña debe tener al menos 8 caracteres.", file=sys.stderr)
        sys.exit(1)

    asyncio.run(create_admin_user(email=email, password=password))


if __name__ == "__main__":
    main()