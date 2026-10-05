from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Optional

from app.core.database import get_db
from app.models.artwork import Watercolor, ArtworkStatus, Category
from app.schemas.artwork import ArtworkSEOResponse, ArtworkListResponse

router = APIRouter()

@router.get("", response_model=ArtworkListResponse, status_code=status.HTTP_200_OK)
async def list_artworks(
    category_slug: Optional[str] = Query(None, description="Filtrar por slug de categoría"),
    status_filter: Optional[ArtworkStatus] = Query(None, description="Filtrar por disponibilidad"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """
    Endpoint público para alimentar el Grid principal de la galería en Nuxt 3.
    Soporta filtrado semántico por categoría (JOIN) y estado de obra.
    """
    query = select(Watercolor)
    count_query = select(func.count(Watercolor.id))

    # 1. Filtrado condicional por Categoría (Requerido en el listado)
    if category_slug:
        query = query.join(Category).where(Category.slug == category_slug)
        count_query = count_query.join(Category).where(Category.slug == category_slug)

    # 2. Filtrado condicional por Estado
    if status_filter:
        query = query.where(Watercolor.status == status_filter)
        count_query = count_query.where(Watercolor.status == status_filter)

    # 3. Conteo total para paginación SSR / Infinite Scroll
    total_res = await db.execute(count_query)
    total = total_res.scalar_one() or 0

    # 4. Paginación y ordenación determinista por fecha de creación
    query = query.offset(offset).limit(limit).order_by(Watercolor.created_at.desc())
    result = await db.execute(query)
    items = result.scalars().all()

    return {
        "total": total,
        "items": items
    }


@router.get("/{slug}", response_model=ArtworkSEOResponse, status_code=status.HTTP_200_OK)
async def get_artwork_by_slug(slug: str, db: AsyncSession = Depends(get_db)):
    """
    Resuelve una obra por su slug único empleando consulta B-Tree.
    Genera payload nativo Schema.org (VisualArtwork) para SSR en Nuxt 3.
    """
    query = select(Watercolor).where(Watercolor.slug == slug)
    result = await db.execute(query)
    artwork = result.scalar_one_or_none()

    if not artwork:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Obra con slug '{slug}' no encontrada"
        )

    # Construcción del esquema Schema.org JSON-LD para SEO dinámico
    json_ld_payload = {
        "@context": "https://schema.org",
        "@type": "VisualArtwork",
        "name": artwork.title,
        "description": artwork.description or artwork.title,
        "artForm": "Pintura",
        "artMedium": "Acuarela",
        "artworkSurface": "Papel de algodón",
        "width": f"{artwork.width_cm} cm" if artwork.width_cm else None,
        "height": f"{artwork.height_cm} cm" if artwork.height_cm else None,
        "image": f"/media/{artwork.image_base_path}.webp",
        "abstract": artwork.alt_text,
        "offers": {
            "@type": "Offer",
            "price": str(artwork.price) if artwork.price else None,
            "priceCurrency": "EUR",
            "availability": (
                "https://schema.org/InStock"
                if artwork.status == ArtworkStatus.DISPONIBLE
                else "https://schema.org/OutOfStock"
            )
        } if artwork.price or artwork.status != ArtworkStatus.DISPONIBLE else None
    }

    # Limpieza de nulos para minificación de payload
    json_ld_payload = {k: v for k, v in json_ld_payload.items() if v is not None}

    return {
        "data": artwork,
        "json_ld": json_ld_payload
    }