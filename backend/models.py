import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Text, DateTime, JSON, Integer, Enum as SAEnum
)
from sqlalchemy.dialects.postgresql import UUID
import enum
from database import Base


class ProductType(str, enum.Enum):
    ac = "ac"
    washing_machine = "washing_machine"
    microwave = "microwave"
    unknown = "unknown"


class TicketStatus(str, enum.Enum):
    open = "open"
    in_progress = "in_progress"
    resolved = "resolved"


# ─────────────────────────────────────────────
#  Knowledge Base Items (RAG source documents)
# ─────────────────────────────────────────────
class KnowledgeItem(Base):
    __tablename__ = "knowledge_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product = Column(SAEnum(ProductType), nullable=False, index=True)
    intent = Column(String(100), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    keywords = Column(JSON, nullable=False, default=list)   # list of trigger keywords
    content = Column(Text, nullable=False)                  # full troubleshooting description
    solution_steps = Column(JSON, nullable=False, default=list)  # ordered list of steps
    severity = Column(String(20), default="medium")         # low / medium / high
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ─────────────────────────────────────────────
#  Conversation Sessions
# ─────────────────────────────────────────────
class ConversationSession(Base):
    __tablename__ = "conversation_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(String(100), unique=True, nullable=False, index=True)
    customer_name = Column(String(100), nullable=True)
    phone_number = Column(String(20), nullable=True)
    product_detected = Column(SAEnum(ProductType), default=ProductType.unknown)
    intent_detected = Column(String(100), nullable=True)
    conversation_history = Column(JSON, default=list)   # list of {role, content, timestamp}
    language_detected = Column(String(20), default="english")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ─────────────────────────────────────────────
#  Service Tickets
# ─────────────────────────────────────────────
class ServiceTicket(Base):
    __tablename__ = "service_tickets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticket_number = Column(String(20), unique=True, nullable=False)
    session_id = Column(String(100), nullable=True)
    customer_name = Column(String(100), nullable=False)
    phone_number = Column(String(20), nullable=False)
    product = Column(SAEnum(ProductType), nullable=False)
    issue_description = Column(Text, nullable=False)
    intent = Column(String(100), nullable=True)
    status = Column(SAEnum(TicketStatus), default=TicketStatus.open)
    resolution_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
