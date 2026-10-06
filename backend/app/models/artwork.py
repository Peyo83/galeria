from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional, List
from enum import Enum
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, DateTime, Numeric, Enum as SQLEnum

class ArtworkStatus(str, Enum):
    DISPONIBLE = "DISPONIBLE"
    RESERVADO = "RESERVADO"
    COLECCION_PRIVADA = "COLECCION_PRIVADA"

class User(SQLModel, table=True):
    __tablename__ = "users"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(max_length=255, unique=True, nullable=False) # Eliminado index=True explícito
    hashed_password: str = Field(max_length=255, nullable=False)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )

class Category(SQLModel, table=True):
    __tablename__ = "categories"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100, unique=True, nullable=False)
    slug: str = Field(max_length=120, unique=True, nullable=False) # Eliminado index=True explícito
    description: Optional[str] = Field(default=None)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )

    watercolors: List["Watercolor"] = Relationship(back_populates="category")

class Watercolor(SQLModel, table=True):
    __tablename__ = "watercolors"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=255, nullable=False)
    slug: str = Field(max_length=280, unique=True, nullable=False) # Eliminado index=True explícito
    description: Optional[str] = Field(default=None)
    width_cm: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(precision=5, scale=2), nullable=True))
    height_cm: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(precision=5, scale=2), nullable=True))
    price: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(precision=10, scale=2), nullable=True))
    image_base_path: str = Field(max_length=512, nullable=False)
    alt_text: str = Field(max_length=255, nullable=False)
    
    # Mapeo correcto al Enum nativo de PostgreSQL
    status: ArtworkStatus = Field(
        default=ArtworkStatus.DISPONIBLE,
        sa_column=Column(
            SQLEnum(ArtworkStatus, name="artwork_status", create_type=False),
            nullable=False,
            default=ArtworkStatus.DISPONIBLE,
            index=True
        )
    )
    
    category_id: Optional[int] = Field(default=None, foreign_key="categories.id", index=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )

    category: Optional[Category] = Relationship(back_populates="watercolors")