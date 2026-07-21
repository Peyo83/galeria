# backend/app/models/artwork.py
from datetime import datetime
from typing import Optional, List
from enum import Enum
from sqlmodel import SQLModel, Field, Relationship

class ArtworkStatus(str, Enum):
    DISPONIBLE = "DISPONIBLE"
    RESERVADO = "RESERVADO"
    COLECCION_PRIVADA = "COLECCION_PRIVADA"

class Category(SQLModel, table=True):
    __tablename__ = "categories"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100, unique=True, nullable=False)
    slug: str = Field(max_length=120, unique=True, nullable=False, index=True)
    description: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    watercolors: List["Watercolor"] = Relationship(back_populates="category")

class Watercolor(SQLModel, table=True):
    __tablename__ = "watercolors"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=255, nullable=False)
    slug: str = Field(max_length=280, unique=True, nullable=False, index=True)
    description: Optional[str] = Field(default=None)
    width_cm: Optional[float] = Field(default=None)
    height_cm: Optional[float] = Field(default=None)
    price: Optional[float] = Field(default=None)
    image_base_path: str = Field(max_length=512, nullable=False)
    alt_text: str = Field(max_length=255, nullable=False)
    status: ArtworkStatus = Field(default=ArtworkStatus.DISPONIBLE, index=True)
    category_id: Optional[int] = Field(default=None, foreign_key="categories.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    category: Optional[Category] = Relationship(back_populates="watercolors")