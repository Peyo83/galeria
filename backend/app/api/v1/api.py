from fastapi import APIRouter
from app.api.v1.routers import admin_artworks, artworks, auth

api_router = APIRouter()

# Authentication (POST /api/v1/auth/token)
api_router.include_router(
    auth.router, 
    prefix="/auth", 
    tags=["Autenticación Admin"]
)

# Catálogo público optimizado para SSR/SEO (GET /api/v1/artworks...)
api_router.include_router(
    artworks.router, 
    prefix="/artworks", 
    tags=["Artworks & SEO (Público)"]
)

# Panel de Administración privado (POST/PUT/DELETE /api/v1/admin/artworks...)
api_router.include_router(
    admin_artworks.router, 
    prefix="/admin/artworks", 
    tags=["Gestión CMS Obras (Protegido)"]
)