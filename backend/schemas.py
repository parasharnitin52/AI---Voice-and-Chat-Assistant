from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime
from uuid import UUID
import enum


class ProductType(str, enum.Enum):
    ac = "ac"
    washing_machine = "washing_machine"
    microwave = "microwave"
    unknown = "unknown"


class TicketStatus(str, enum.Enum):
    open = "open"
    in_progress = "in_progress"
    resolved = "resolved"


# ─── Chat ───────────────────────────────────
class ChatMessage(BaseModel):
    role: str   # "user" | "assistant"
    content: str
    timestamp: Optional[str] = None


class ChatRequest(BaseModel):
    session_id: str
    message: str
    customer_name: Optional[str] = None
    phone_number: Optional[str] = None


class ChatResponse(BaseModel):
    session_id: str
    response: str
    product_detected: str
    intent_detected: Optional[str] = None
    language_detected: str
    suggest_ticket: bool = False
    conversation_history: List[ChatMessage] = []


# ─── Transcription ──────────────────────────
class TranscribeResponse(BaseModel):
    transcript: str
    language: str
    duration: Optional[float] = None


# ─── Tickets ────────────────────────────────
class CreateTicketRequest(BaseModel):
    session_id: Optional[str] = None
    customer_name: str = Field(..., min_length=2)
    phone_number: str = Field(..., min_length=10)
    product: ProductType
    issue_description: str = Field(..., min_length=10)
    intent: Optional[str] = None


class TicketResponse(BaseModel):
    id: UUID
    ticket_number: str
    customer_name: str
    phone_number: str
    product: str
    issue_description: str
    intent: Optional[str]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Knowledge Upload ───────────────────────
class KnowledgeItemCreate(BaseModel):
    product: ProductType
    intent: str
    title: str
    keywords: List[str]
    content: str
    solution_steps: List[str]
    severity: str = "medium"


class KnowledgeItemResponse(BaseModel):
    id: UUID
    product: str
    intent: str
    title: str
    content: str
    solution_steps: List[str]
    severity: str

    class Config:
        from_attributes = True


# ─── Session ────────────────────────────────
class SessionResponse(BaseModel):
    session_id: str
    product_detected: str
    intent_detected: Optional[str]
    language_detected: str
    conversation_history: List[ChatMessage]
    created_at: datetime

    class Config:
        from_attributes = True
