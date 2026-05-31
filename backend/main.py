"""
Customer Support Voice Agent — FastAPI Backend
ElectroServ | AC · Washing Machine · Microwave
"""
import uuid
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from config import get_settings
from database import get_db, init_db
from models import (
    ConversationSession, ServiceTicket, KnowledgeItem,
    ProductType as DBProductType, TicketStatus,
)
from schemas import (
    ChatRequest, ChatResponse, ChatMessage,
    TranscribeResponse,
    CreateTicketRequest, TicketResponse,
    KnowledgeItemCreate, KnowledgeItemResponse,
    SessionResponse,
)
from groq_client import transcribe_audio, chat_completion
from knowledge_base import (
    detect_product, detect_intent, detect_language,
    retrieve_knowledge, build_system_prompt,
)

settings = get_settings()

app = FastAPI(
    title="ElectroServ Voice Support API",
    description="AI-powered voice customer support for AC, Washing Machine & Microwave",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    init_db()
    print("🚀 ElectroServ Voice API is running!")


# ─────────────────────────────────────────────
#  Health
# ─────────────────────────────────────────────
@app.get("/health")
def health_check():
    return {"status": "ok", "service": "ElectroServ Voice Support API"}


# ─────────────────────────────────────────────
#  POST /api/transcribe  — Audio → Text
# ─────────────────────────────────────────────
@app.post("/api/transcribe", response_model=TranscribeResponse)
async def transcribe(
    audio: UploadFile = File(...),
):
    """
    Accepts an audio file (webm/wav/mp3/ogg) and returns the transcript
    via Groq Whisper large-v3.
    """
    if not audio.content_type or not any(
        t in audio.content_type for t in ["audio", "video", "octet-stream"]
    ):
        raise HTTPException(400, "File must be an audio file.")

    audio_bytes = await audio.read()
    print(f"[DEBUG] Received audio file: {audio.filename}, Content-Type: {audio.content_type}, Size: {len(audio_bytes)} bytes")
    if len(audio_bytes) < 100:
        raise HTTPException(400, "Audio file is too short or empty.")

    try:
        result = transcribe_audio(audio_bytes, filename=audio.filename or "audio.webm")
        return TranscribeResponse(**result)
    except Exception as e:
        import logging
        logging.error(f"Transcription failed: {e}")
        # Try to extract message if it's a Groq APIStatusError
        detail = getattr(e, "message", str(e))
        status_code = getattr(e, "status_code", 400)
        raise HTTPException(status_code=status_code, detail=f"STT Error: {detail}")


# ─────────────────────────────────────────────
#  POST /api/chat  — Text → AI Response
# ─────────────────────────────────────────────
@app.post("/api/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
):
    """
    Main chat endpoint. Accepts user text + session_id.
    Performs product/intent/language detection, RAG retrieval,
    and returns Groq LLaMA response.
    """
    # ── 1. Load or create session ──────────────
    session = db.query(ConversationSession).filter_by(
        session_id=request.session_id
    ).first()

    if not session:
        session = ConversationSession(
            session_id=request.session_id,
            conversation_history=[],
        )
        db.add(session)

    # ── 2. Detect product / intent / language ──
    full_text = request.message
    # Also check conversation history context for better detection
    history_text = " ".join(
        m.get("content", "") for m in (session.conversation_history or [])
    )
    combined_text = f"{history_text} {full_text}"

    product = detect_product(combined_text)
    intent = detect_intent(full_text)
    language = detect_language(full_text)

    # Persist detections to session
    if product != DBProductType.unknown:
        session.product_detected = product
    if intent:
        session.intent_detected = intent
    if language:
        session.language_detected = language

    # Use session's remembered product if current message doesn't have one
    effective_product = (
        product if product != DBProductType.unknown else (session.product_detected or DBProductType.unknown)
    )

    # ── 3. RAG retrieval ───────────────────────
    knowledge_items = retrieve_knowledge(db, effective_product, intent, full_text)

    # ── 4. Build system prompt ─────────────────
    system_prompt = build_system_prompt(
        effective_product, intent or session.intent_detected,
        language or session.language_detected or "english",
        knowledge_items,
    )

    # ── 5. Build message history for LLM ───────
    history = session.conversation_history or []
    llm_messages = [
        {"role": m["role"], "content": m["content"]}
        for m in history[-10:]  # last 10 messages for context
    ]
    llm_messages.append({"role": "user", "content": full_text})

    # ── 6. Call Groq LLaMA ─────────────────────
    try:
        ai_response = chat_completion(llm_messages, system_prompt)
    except Exception as e:
        import logging
        logging.error(f"Chat completion failed: {e}")
        detail = getattr(e, "message", str(e))
        status_code = getattr(e, "status_code", 400)
        raise HTTPException(status_code=status_code, detail=f"LLM Error: {detail}")

    # ── 7. Update session history ──────────────
    now = datetime.utcnow().isoformat()
    history.append({"role": "user", "content": full_text, "timestamp": now})
    history.append({"role": "assistant", "content": ai_response, "timestamp": now})
    session.conversation_history = history
    session.updated_at = datetime.utcnow()

    # Update customer info if provided
    if request.customer_name:
        session.customer_name = request.customer_name
    if request.phone_number:
        session.phone_number = request.phone_number

    db.commit()

    # ── 8. Decide if ticket should be suggested ─
    exchange_count = len([m for m in history if m["role"] == "user"])
    suggest_ticket = exchange_count >= 3 and effective_product != DBProductType.unknown

    return ChatResponse(
        session_id=request.session_id,
        response=ai_response,
        product_detected=effective_product.value,
        intent_detected=intent or session.intent_detected,
        language_detected=language or session.language_detected or "english",
        suggest_ticket=suggest_ticket,
        conversation_history=[
            ChatMessage(role=m["role"], content=m["content"], timestamp=m.get("timestamp"))
            for m in history
        ],
    )


# ─────────────────────────────────────────────
#  POST /api/tickets  — Create Service Ticket
# ─────────────────────────────────────────────
@app.post("/api/tickets", response_model=TicketResponse)
def create_ticket(
    request: CreateTicketRequest,
    db: Session = Depends(get_db),
):
    """Create a new service ticket."""
    # Generate ticket number: ST-YYYYMMDD-XXXX
    date_str = datetime.utcnow().strftime("%Y%m%d")
    short_id = str(uuid.uuid4()).split("-")[0].upper()
    ticket_number = f"ST-{date_str}-{short_id}"

    ticket = ServiceTicket(
        ticket_number=ticket_number,
        session_id=request.session_id,
        customer_name=request.customer_name,
        phone_number=request.phone_number,
        product=request.product,
        issue_description=request.issue_description,
        intent=request.intent,
        status=TicketStatus.open,
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


# ─────────────────────────────────────────────
#  GET /api/tickets  — List All Tickets
# ─────────────────────────────────────────────
@app.get("/api/tickets", response_model=list[TicketResponse])
def list_tickets(
    status: str | None = None,
    product: str | None = None,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    query = db.query(ServiceTicket)
    if status:
        query = query.filter(ServiceTicket.status == status)
    if product:
        query = query.filter(ServiceTicket.product == product)
    tickets = query.order_by(ServiceTicket.created_at.desc()).limit(limit).all()
    return tickets


# ─────────────────────────────────────────────
#  GET /api/session/{session_id}
# ─────────────────────────────────────────────
@app.get("/api/session/{session_id}", response_model=SessionResponse)
def get_session(session_id: str, db: Session = Depends(get_db)):
    session = db.query(ConversationSession).filter_by(session_id=session_id).first()
    if not session:
        raise HTTPException(404, "Session not found.")
    return session


# ─────────────────────────────────────────────
#  POST /api/knowledge  — Upload Knowledge Item
# ─────────────────────────────────────────────
@app.post("/api/knowledge", response_model=KnowledgeItemResponse)
def add_knowledge_item(
    item: KnowledgeItemCreate,
    db: Session = Depends(get_db),
):
    knowledge = KnowledgeItem(**item.model_dump())
    db.add(knowledge)
    db.commit()
    db.refresh(knowledge)
    return knowledge


@app.get("/api/knowledge", response_model=list[KnowledgeItemResponse])
def list_knowledge(
    product: str | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(KnowledgeItem)
    if product:
        query = query.filter(KnowledgeItem.product == product)
    return query.all()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
