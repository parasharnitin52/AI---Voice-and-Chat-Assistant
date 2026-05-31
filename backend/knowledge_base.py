"""
Knowledge Base module — retrieves relevant troubleshooting content
from PostgreSQL to inject as RAG context into the LLM prompt.
"""
import re
from sqlalchemy.orm import Session
from models import KnowledgeItem, ProductType


# ─────────────────────────────────────────────
#  Product Detection
# ─────────────────────────────────────────────
PRODUCT_KEYWORDS = {
    ProductType.ac: [
        "ac", "air conditioner", "air conditioning", "aircon", "cooler",
        "cooling", "ek", "a/c", "वातानुकूलक", "एसी",
    ],
    ProductType.washing_machine: [
        "washing machine", "washer", "laundry", "washing", "wash",
        "dryer", "spin", "kapde", "कपड़े", "वाशिंग मशीन",
    ],
    ProductType.microwave: [
        "microwave", "oven", "micro wave", "microwave oven",
        "heating", "bake", "माइक्रोवेव", "ओवन",
    ],
}

INTENT_KEYWORDS = {
    # AC intents
    "not_cooling": ["not cooling", "nahi thanda", "thanda nahi", "warm air", "hot air",
                    "cooling nahi", "ठंडा नहीं", "not cold"],
    "water_leakage": ["water leak", "paani aa raha", "drip", "leaking", "पानी टपक",
                      "wet floor", "water dripping", "paani tha rha"],
    "remote_not_working": ["remote", "remote not working", "remote kaam nahi",
                           "रिमोट", "controller", "not responding"],
    "not_spinning": ["not spinning", "spin nahi", "spin nahi ho raha", "spin nhi",
                     "drum not moving", "not rotating", "ड्रम नहीं घूम"],
    "not_draining": ["not draining", "drain nahi", "water not going", "paani nahi ja",
                     "पानी नहीं जा रहा", "stuck water"],
    "door_lock_issue": ["door", "door not opening", "door locked", "lock", "darwaza",
                        "दरवाज़ा", "latch", "door lock"],
    "not_heating": ["not heating", "garam nahi", "heat nahi", "not warm",
                    "गरम नहीं", "food not hot", "microwave not working"],
    "turntable_issue": ["turntable", "plate not rotating", "plate stuck", "rotating plate",
                        "थाली", "ghoomna", "घूमना"],
    "display_issue": ["display", "screen", "error on screen", "display off",
                      "display not working", "डिस्प्ले"],
    "power_issue": ["power", "not turning on", "not starting", "on nahi ho raha",
                    "बंद", "शुरू नहीं", "no power", "dead", "start nahi"],
    "noise_issue": ["noise", "sound", "noisy", "rattling", "vibration", "awaz",
                    "आवाज़", "loud", "grinding", "shaking"],
    "error_code": ["error", "error code", "E1", "E2", "F1", "blinking", "flashing",
                   "code", "एरर"],
}


def detect_product(text: str) -> ProductType:
    text_lower = text.lower()
    for product, keywords in PRODUCT_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                return product
    return ProductType.unknown


def detect_intent(text: str) -> str | None:
    text_lower = text.lower()
    for intent, keywords in INTENT_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                return intent
    return None


def detect_language(text: str) -> str:
    """Rough heuristic — detect Hindi/Hinglish vs English."""
    hindi_chars = len(re.findall(r"[\u0900-\u097F]", text))
    hinglish_words = ["nahi", "hai", "mera", "meri", "karo", "kaam", "nhi",
                      "ho", "raha", "kar", "tha", "rhi", "hain"]
    hinglish_count = sum(1 for w in hinglish_words if w in text.lower().split())

    if hindi_chars > 3:
        return "hindi"
    elif hinglish_count >= 2:
        return "hinglish"
    return "english"


# ─────────────────────────────────────────────
#  RAG Retrieval from PostgreSQL
# ─────────────────────────────────────────────
def retrieve_knowledge(
    db: Session,
    product: ProductType,
    intent: str | None,
    text: str,
    top_k: int = 3,
) -> list[KnowledgeItem]:
    """
    Fetch the most relevant knowledge items from PostgreSQL.
    Priority: exact product + intent match → product-only match.
    """
    if product == ProductType.unknown:
        return []

    query = db.query(KnowledgeItem).filter(KnowledgeItem.product == product)

    if intent:
        exact = query.filter(KnowledgeItem.intent == intent).limit(top_k).all()
        if exact:
            return exact

    # Fallback: keyword match in title/content
    text_lower = text.lower()
    all_items = query.all()
    scored = []
    for item in all_items:
        score = sum(1 for kw in (item.keywords or []) if kw.lower() in text_lower)
        if score > 0:
            scored.append((score, item))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [item for _, item in scored[:top_k]]


# ─────────────────────────────────────────────
#  System Prompt Builder
# ─────────────────────────────────────────────
def build_system_prompt(
    product: ProductType,
    intent: str | None,
    language: str,
    knowledge_items: list[KnowledgeItem],
) -> str:
    product_display = {
        ProductType.ac: "Air Conditioner (AC)",
        ProductType.washing_machine: "Washing Machine",
        ProductType.microwave: "Microwave Oven",
        ProductType.unknown: "Unknown",
    }.get(product, "Unknown")

    lang_instruction = {
        "hindi": "Respond ONLY in Hindi (Devanagari script).",
        "hinglish": "Respond in Hinglish (mix of Hindi and English, using Roman script for Hindi words).",
        "english": "Respond in clear, simple English.",
    }.get(language, "Respond in English.")

    knowledge_context = ""
    if knowledge_items:
        knowledge_context = "\n\n## Retrieved Knowledge Base Context:\n"
        for i, item in enumerate(knowledge_items, 1):
            steps = "\n".join(f"  {j}. {s}" for j, s in enumerate(item.solution_steps, 1))
            knowledge_context += f"""
### [{i}] {item.title}
{item.content}
**Troubleshooting Steps:**
{steps}
"""

    unsupported_msg = (
        "I currently support only ACs, washing machines, and microwave ovens."
        if language == "english"
        else "Main sirf AC, washing machine aur microwave oven ke liye support karta hoon."
    )

    return f"""You are a helpful, friendly customer support voice agent for ElectroServ — an electronics company.
You specialize in: Air Conditioners (AC), Washing Machines, and Microwave Ovens.

## Current Context:
- Product: {product_display}
- Detected Issue: {intent or "Not yet identified"}
- Language Mode: {language}

## Language Rule:
{lang_instruction}

## Rules:
1. NEVER make up product information or model numbers not provided.
2. ALWAYS use the knowledge base context below when available.
3. If the product is NOT an AC, washing machine, or microwave, say: "{unsupported_msg}"
4. Keep responses SHORT and CONVERSATIONAL (2–4 sentences max for voice).
5. If the issue seems unresolved after 2 exchanges, suggest creating a service ticket.
6. Ask for customer name and phone number only when creating a ticket.
7. Be empathetic — customers are frustrated when appliances break.
{knowledge_context}
"""
