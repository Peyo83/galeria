from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.v1.api import api_router
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# Servir imágenes optimizadas procesadas (WebP/AVIF)
app.mount("/media", StaticFiles(directory="media"), name="media")

# CORS adaptado para Nuxt 3 (SSR + Hydration CSR)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,  # Recomendado usar lista configurable desde Settings
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Un solo punto de montaje para todos los routers v1
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health", tags=["Infrastructure"])
async def health_check():
    return {"status": "healthy", "version": settings.VERSION}