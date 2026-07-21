# backend/app/api/v1/routers/chat.py
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel.ext.asyncio.session import AsyncSession
from app.core.database import get_db
from app.services.agent import ArtGalleryAgent

router = APIRouter()
agent_service = ArtGalleryAgent()

class ChatRequest(BaseModel):
    session_id: str
    message: str

class ChatResponse(BaseModel):
    response: str

@router.post("/message", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def process_agent_message(payload: ChatRequest, db: AsyncSession = Depends(get_db)):
    """
    Ingesta interacciones conversacionales entrantes.
    Mantiene memoria en Postgres e infiere intenciones comerciales.
    """
    try:
        reply = await agent_service.execute(
            db=db,
            session_id=payload.session_id,
            user_input=payload.message
        )
        return {"response": reply}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en la ejecución del Agente conversacional: {str(e)}"
        )