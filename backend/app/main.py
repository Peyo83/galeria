# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.routers import artworks, chat

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Configuración de CORS estricta preparada para el Frontend SSR en Nuxt 3
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Ajustar a dominios específicos en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registro de Routers de la API
app.include_router(
    artworks.router,
    prefix=f"{settings.API_V1_STR}/artworks",
    tags=["Artworks & SEO"]
)

app.include_router(
    chat.router,
    prefix=f"{settings.API_V1_STR}/chat",
    tags=["Conversational AI Agent"]
)

@app.get("/health", tags=["Infrastructure"])
async def health_check():
    return {"status": "healthy", "version": settings.VERSION}