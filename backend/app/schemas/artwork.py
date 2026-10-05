from pydantic import BaseModel, ConfigDict
from typing import Dict, Any, Optional, List
from datetime import datetime
from decimal import Decimal
from app.models.artwork import ArtworkStatus

class WatercolorBase(BaseModel):
    title: str
    slug: str
    description: Optional[str] = None
    width_cm: Optional[Decimal] = None
    height_cm: Optional[Decimal] = None
    price: Optional[Decimal] = None
    image_base_path: str
    alt_text: str
    status: ArtworkStatus = ArtworkStatus.DISPONIBLE
    category_id: Optional[int] = None

class WatercolorRead(WatercolorBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ArtworkSEOResponse(BaseModel):
    data: WatercolorRead
    json_ld: Dict[str, Any]

class ArtworkListResponse(BaseModel):
    total: int
    items: List[WatercolorRead]