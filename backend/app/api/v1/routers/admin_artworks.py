import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.artwork import Watercolor, ArtworkStatus, User
from app.schemas.artwork import WatercolorRead
from app.services.image import save_and_process_image, delete_artwork_images

router = APIRouter()

@router.post("", response_model=WatercolorRead, status_code=status.HTTP_201_CREATED)
async def create_artwork(
    title: str = Form(...),
    slug: str = Form(...),
    description: Optional[str] = Form(None),
    width_cm: Optional[float] = Form(None),
    height_cm: Optional[float] = Form(None),
    price: Optional[float] = Form(None),
    alt_text: str = Form(...),
    status_val: ArtworkStatus = Form(ArtworkStatus.DISPONIBLE, alias="status"),
    category_id: Optional[int] = Form(None),
    image: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Crea una obra nueva procesando su imagen física a formato WebP optimizado."""
    # Verificar slug único
    existing_slug = await db.execute(select(Watercolor).where(Watercolor.slug == slug))
    if existing_slug.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El slug especificado ya está registrado."
        )

    # Validar Content-Type
    if image.content_type not in ["image/jpeg", "image/png", "image/webp"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato de imagen no soportado. Debe ser JPEG, PNG o WebP."
        )

    # Generar nombre base de archivo
    unique_id = uuid.uuid4().hex[:8]
    base_filename = f"{slug}-{unique_id}"
    
    file_bytes = await image.read()
    image_base_path = await save_and_process_image(file_bytes, base_filename)

    artwork = Watercolor(
        title=title,
        slug=slug,
        description=description,
        width_cm=width_cm,
        height_cm=height_cm,
        price=price,
        image_base_path=image_base_path,
        alt_text=alt_text,
        status=status_val,
        category_id=category_id
    )

    db.add(artwork)
    await db.commit()
    await db.refresh(artwork)

    return artwork


@router.delete("/{artwork_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_artwork(
    artwork_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Elimina la obra de la BD y borra sus archivos de imagen físicos en disco."""
    query = select(Watercolor).where(Watercolor.id == artwork_id)
    result = await db.execute(query)
    artwork = result.scalar_one_or_none()

    if not artwork:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Obra no encontrada."
        )

    await delete_artwork_images(artwork.image_base_path)
    await db.delete(artwork)
    await db.commit()
    return None