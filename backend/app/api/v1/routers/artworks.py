# backend/app/api/v1/routers/artworks.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.core.database import get_db
from app.models.artwork import Watercolor
from app.schemas.artwork import ArtworkSEOResponse

router = APIRouter()

@router.get("/{slug}", response_model=ArtworkSEOResponse, status_code=status.HTTP_200_OK)
async def get_artwork_by_slug(slug: str, db: AsyncSession = Depends(get_db)):
    """
    Resuelve una obra por su slug único empleando escaneo indexado B-Tree.
    Inyecta dinámicamente el esquema de metadatos estructurados VisualArtwork.
    """
    query = select(Watercolor).where(Watercolor.slug == slug)
    result = await db.execute(query)
    artwork = result.scalar_one_or_none()
    
    if not artwork:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Artwork with slug '{slug}' not found"
        )
    
    # Construcción semántica nativa del esquema Schema.org (VisualArtwork)
    json_ld_payload = {
        "@context": "https://schema.org",
        "@type": "VisualArtwork",
        "name": artwork.title,
        "description": artwork.description or "",
        "artform": "watercolor painting",
        "artMedium": "watercolor",
        "artworkSurface": "paper",
        "width": f"{artwork.width_cm} cm" if artwork.width_cm else None,
        "height": f"{artwork.height_cm} cm" if artwork.height_cm else None,
        "image": f"{artwork.image_base_path}.webp",
        "abstract": artwork.alt_text,
        "offers": {
            "@type": "Offer",
            "price": str(artwork.price) if artwork.price else None,
            "priceCurrency": "EUR",
            "availability": (
                "https://schema.org/InStock" 
                if artwork.status == "DISPONIBLE" 
                else "https://schema.org/OutOfStock"
            )
        } if artwork.price or artwork.status != "DISPONIBLE" else None
    }
    
    # Sanitización de claves nulas para reducir tamaño de payload en red
    json_ld_payload = {k: v for k, v in json_ld_payload.items() if v is not None}

    return {
        "data": artwork,
        "json_ld": json_ld_payload
    }