# backend/app/services/agent.py
import json
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import convert_to_openai_messages, BaseMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI

from app.models.chat import AIChatSession, PurchaseLead
from app.models.artwork import Watercolor

# Esquema estricto para forzar al LLM a clasificar la intención comercial y extraer entidades
class PurchaseIntentDetector(BaseModel):
    has_purchase_intent: bool = Field(
        description="Verdadero si el usuario muestra interés explícito en comprar, reservar, o preguntar precios de una obra específica."
    )
    target_watercolor_slug: Optional[str] = Field(
        default=None,
        description="El slug exacto de la acuarela sobre la cual está interesado (ej: 'atardecer-en-la-alcarria'). Si no se menciona o no se deduce con seguridad, dejar nulo."
    )
    notes: Optional[str] = Field(
        default=None,
        description="Resumen conciso del motivo de compra, dudas expresadas o detalles de contacto provistos voluntariamente."
    )

class ArtGalleryAgent:
    def __init__(self, model_name: str = "gpt-4o-mini", temperature: float = 0.2):
        self.llm = ChatOpenAI(model=model_name, temperature=temperature)
        # Enlazamos la herramienta de detección estructurada de forma nativa al LLM
        self.detector_llm = self.llm.with_structured_output(PurchaseIntentDetector)
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", (
                "Eres el curador y gestor automatizado experto de la galería de arte en acuarelas. "
                "Tu objetivo es dar información estética, poética y detallada sobre las obras disponibles "
                "y guiar de manera sutil pero efectiva al usuario hacia la adquisición o reserva de las piezas. "
                "Mantén un tono minimalista, sofisticado, culto y muy servicial. "
                "Si te preguntan por una obra que no está en el catálogo, indica amablemente que no está disponible."
            )),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}")
        ])

    async def _load_session_history(self, db: AsyncSession, session_id: str) -> List[BaseMessage]:
        """Carga el historial persistido en JSONB y lo mapea a objetos de mensaje de LangChain."""
        query = select(AIChatSession).where(AIChatSession.session_id == session_id)
        result = await db.execute(query)
        session_record = result.scalar_one_or_none()
        
        if not session_record:
            return []
            
        messages = []
        for msg in session_record.chat_history:
            if msg.get("type") == "human":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg.get("type") == "ai":
                messages.append(AIMessage(content=msg["content"]))
        return messages

    async def _save_session_history(self, db: AsyncSession, session_id: str, history: List[Dict[str, str]]):
        """Persiste de forma asíncrona la lista serializada en la columna JSONB."""
        query = select(AIChatSession).where(AIChatSession.session_id == session_id)
        result = await db.execute(query)
        session_record = result.scalar_one_or_none()
        
        if not session_record:
            session_record = AIChatSession(session_id=session_id, chat_history=history)
            db.add(session_record)
        else:
            session_record.chat_history = history
            session_record.updated_at = datetime.utcnow()
            db.add(session_record)
            
        await db.commit()

    async def _get_catalog_context(self, db: AsyncSession) -> str:
        """Extrae el catálogo activo optimizado con slugs para inyectar contexto dinámico al agente."""
        query = select(Watercolor).where(Watercolor.status == "DISPONIBLE")
        result = await db.execute(query)
        artworks = result.scalars().all()
        
        ctx = "Catálogo de Obras Disponibles actualmente:\n"
        for art in artworks:
            ctx += f"- Título: {art.title} | Slug: {art.slug} | Dimensiones: {art.width_cm}x{art.height_cm}cm | Precio: {art.price} EUR | Descripción: {art.description}\n"
        return ctx

    async def execute(self, db: AsyncSession, session_id: str, user_input: str) -> str:
        """
        Punto de entrada asíncrono.
        Procesa el flujo conversacional, interactúa con el LLM y dispara la detección de leads.
        """
        # 1. Recuperar contexto histórico y catálogo dinámico de base de datos
        history_messages = await self._load_session_history(db, session_id)
        catalog_ctx = await self._get_catalog_context(db)
        
        # 2. Enriquecer el input con el contexto actual del catálogo sin ensuciar la memoria limpia
        enriched_system_prompt = self.prompt.format_messages(
            history=history_messages,
            input=f"[CONTEXTO ACTUAL DEL CATÁLOGO DE LA GALERÍA]\n{catalog_ctx}\n\nMensaje del Usuario: {user_input}"
        )
        
        # 3. Invocar la generación conversacional
        ai_response = await self.llm.ainvoke(enriched_system_prompt)
        ai_content = str(ai_response.content)
        
        # 4. Actualizar y serializar el historial conversacional nativo en formato estructurado JSONB
        updated_history_serialized = []
        for msg in history_messages:
            type_str = "human" if isinstance(msg, HumanMessage) else "ai"
            updated_history_serialized.append({"type": type_str, "content": msg.content})
            
        updated_history_serialized.append({"type": "human", "content": user_input})
        updated_history_serialized.append({"type": "ai", "content": ai_content})
        
        await self._save_session_history(db, session_id, updated_history_serialized)
        
        # 5. Pipeline Asíncrono en segundo plano: Detección y clasificación de la intención comercial
        # Pasamos el hilo completo de la sesión actual al detector especializado
        full_conversation_ctx = [HumanMessage(content=m["content"]) if m["type"]=="human" else AIMessage(content=m["content"]) for m in updated_history_serialized]
        
        try:
            detection: PurchaseIntentDetector = await self.detector_llm.ainvoke(full_conversation_ctx)
            if detection.has_purchase_intent:
                await self._register_purchase_lead(db, session_id, detection)
        except Exception:
            # Silenciar o enviar a logs asíncronos para evitar romper el flujo principal de chat del usuario
            pass
            
        return ai_content

    async def _register_purchase_lead(self, db: AsyncSession, session_id: str, detection: PurchaseIntentDetector):
        """Valida e inserta de forma segura un Lead comercial calificado en purchase_leads."""
        if not detection.target_watercolor_slug:
            return
            
        # Validar existencia real de la obra por slug indexado
        art_query = select(Watercolor).where(Watercolor.slug == detection.target_watercolor_slug)
        art_res = await db.execute(art_query)
        artwork = art_res.scalar_one_or_none()
        
        if not artwork:
            return
            
        # Verificar duplicados activos para no saturar los disparadores de la Fase 3
        lead_query = select(PurchaseLead).where(
            PurchaseLead.session_id == session_id,
            PurchaseLead.watercolor_id == artwork.id,
            PurchaseLead.status == "PENDIENTE_CONTACTO"
        )
        lead_res = await db.execute(lead_query)
        existing_lead = lead_res.scalar_one_or_none()
        
        if not existing_lead:
            new_lead = PurchaseLead(
                session_id=session_id,
                watercolor_id=artwork.id,
                customer_contact=session_id,  # El session_id mapea el identificador de origen (ej: whatsapp:+34...)
                status="PENDIENTE_CONTACTO",
                notes=detection.notes
            )
            db.add(new_lead)
            await db.commit()