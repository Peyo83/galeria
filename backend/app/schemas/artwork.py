# backend/app/schemas/artwork.py
from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime
from app.models.artwork import ArtworkStatus

class WatercolorRead(BaseModel):
    id: int
    title: str
    slug: str
    description: Optional[str]
    width_cm: Optional[float]
    height_cm: Optional[float]
    price: Optional[float]
    image_base_path: str
    alt_text: str
    status: ArtworkStatus
    category_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ArtworkSEOResponse(BaseModel):
    data: WatercolorRead
    json_ld: Dict[str, Any]