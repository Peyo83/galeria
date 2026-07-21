# backend/app/models/chat.py
from datetime import datetime
from typing import Optional, Any, Dict
from sqlmodel import SQLModel, Field
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB

class AIChatSession(SQLModel, table=True):
    __tablename__ = "ai_chat_sessions"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: str = Field(max_length=100, unique=True, nullable=False, index=True)
    # Declaración explícita del tipo nativo JSONB para el historial transaccional de LangChain
    chat_history: list = Field(default=[], sa_column=Column(JSONB, nullable=False, server_default='[]'))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class PurchaseLead(SQLModel, table=True):
    __tablename__ = "purchase_leads"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: str = Field(max_length=100, foreign_key="ai_chat_sessions.session_id", nullable=False)
    watercolor_id: int = Field(foreign_key="watercolors.id", nullable=False)
    customer_contact: str = Field(max_length=100, nullable=False)
    status: str = Field(default="PENDIENTE_CONTACTO", max_length=50)
    notes: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)