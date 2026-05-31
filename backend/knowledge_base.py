"""
Knowledge base helpers for product detection, retrieval, and prompt building.
"""
import re
from sqlalchemy.orm import Session
from models import KnowledgeItem, ProductType


PRODUCT_KEYWORDS = {
    ProductType.ac: [
        "ac", "air conditioner", "air conditioning", "aircon", "cooler",
        "cooling", "a/c", "वातानुकूलक", "एसी", "ए सी", "ए.सी", "ए.सी.",
    ],
    ProductType.washing_machine: [
        "washing machine", "washer", "laundry", "washing", "wash",
        "dryer", "spin", "kapde", "कपड़े", "कपडे", "वॉशिंग मशीन",
        "वाशिंग मशीन", "machine", "मशीन",
    ],
    ProductType.microwave: [
        "microwave", "oven", "micro wave", "microwave oven",
        "heating", "bake", "माइक्रोवेव", "ओवन",
    ],
}

INTENT_KEYWORDS = {
    "not_cooling": [
        "not cooling", "nahi thanda", "thanda nahi", "warm air", "hot air",
        "cooling nahi", "cooling nhi", "cool nahi", "cool nhi",
        "thanda nhi", "ठंडा नहीं", "ठंडा नही", "कूलिंग नहीं", "not cold",
    ],
    "water_leakage": [
        "water leak", "paani aa raha", "pani aa raha", "drip", "leaking",
        "wet floor", "water dripping", "paani tapak", "pani tapak",
        "paani leak", "pani leak", "पानी टपक", "पानी आ रहा", "लीक",
    ],
    "remote_not_working": [
        "remote", "remote not working", "remote kaam nahi", "remote kaam nhi",
        "रिमोट", "controller", "not responding",
    ],
    "not_spinning": [
        "not spinning", "spin nahi", "spin nahi ho raha", "spin nhi",
        "drum not moving", "not rotating", "ड्रम नहीं घूम", "घूम नहीं",
        "ghoom nahi", "ghum nahi",
    ],
    "not_draining": [
        "not draining", "drain nahi", "water not going", "paani nahi ja",
        "pani nahi nikal", "paani nahi nikal", "पानी नहीं जा रहा",
        "पानी नहीं निकल", "पानी नहीं निकाल", "stuck water",
    ],
    "door_lock_issue": [
        "door", "door not opening", "door locked", "lock", "darwaza",
        "darwaja", "दरवाज़ा", "दरवाजा", "latch", "door lock",
    ],
    "not_heating": [
        "not heating", "garam nahi", "garam nhi", "heat nahi", "heat nhi",
        "not warm", "गरम नहीं", "गर्म नहीं", "food not hot",
        "microwave not working",
    ],
    "turntable_issue": [
        "turntable", "plate not rotating", "plate stuck", "rotating plate",
        "थाली", "ghoomna", "घूमना", "plate nahi ghoom",
    ],
    "display_issue": [
        "display", "screen", "error on screen", "display off",
        "display not working", "डिस्प्ले", "स्क्रीन",
    ],
    "power_issue": [
        "power", "not turning on", "not starting", "on nahi ho raha",
        "on nhi ho raha", "बंद", "शुरू नहीं", "चालू नहीं",
        "no power", "dead", "start nahi",
    ],
    "noise_issue": [
        "noise", "sound", "noisy", "rattling", "vibration", "awaz", "awaaz",
        "आवाज़", "आवाज", "loud", "grinding", "shaking",
    ],
    "error_code": [
        "error", "error code", "e1", "e2", "f1", "blinking", "flashing",
        "code", "एरर",
    ],
}


def detect_product(text: str) -> ProductType:
    text_lower = text.lower()
    for product, keywords in PRODUCT_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in text_lower:
                return product
    return ProductType.unknown


def detect_intent(text: str) -> str | None:
    text_lower = text.lower()
    for intent, keywords in INTENT_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in text_lower:
                return intent
    return None


def detect_language(text: str) -> str:
    """Detect Hindi, Hinglish, or English from transcribed text."""
    if re.search(r"[\u0900-\u097F]", text):
        return "hindi"

    words = re.findall(r"[a-zA-Z]+", text.lower())
    hinglish_words = {
        "nahi", "nhi", "nahin", "hai", "hain", "mera", "meri", "mere",
        "karo", "kaam", "ho", "raha", "rahi", "rha", "rhi", "kar",
        "tha", "thi", "paani", "pani", "garam", "thanda", "kapde",
        "darwaza", "darwaja", "awaz", "awaaz", "ghoom", "ghum", "chalu",
        "band", "nikal", "aa", "se", "me", "mein", "ka", "ki", "ke",
    }
    if any(word in hinglish_words for word in words):
        return "hinglish"

    return "english"


def retrieve_knowledge(
    db: Session,
    product: ProductType,
    intent: str | None,
    text: str,
    top_k: int = 3,
) -> list[KnowledgeItem]:
    """
    Fetch the most relevant knowledge items from PostgreSQL.
    Priority: exact product + intent match, then keyword match.
    """
    if product == ProductType.unknown:
        return []

    query = db.query(KnowledgeItem).filter(KnowledgeItem.product == product)

    if intent:
        exact = query.filter(KnowledgeItem.intent == intent).limit(top_k).all()
        if exact:
            return exact

    text_lower = text.lower()
    all_items = query.all()
    scored = []
    for item in all_items:
        score = sum(1 for kw in (item.keywords or []) if kw.lower() in text_lower)
        if score > 0:
            scored.append((score, item))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [item for _, item in scored[:top_k]]


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
        "hindi": "Respond ONLY in Hindi using Devanagari script. Never use Urdu, Arabic, or Persian script.",
        "hinglish": (
            "Respond in natural Hinglish using Roman script, mixing Hindi and "
            "simple English words the way an Indian customer support agent would. "
            "Never use Urdu, Arabic, Persian, or any non-Roman script."
        ),
        "english": "Respond in clear, simple English using Roman letters only.",
    }.get(language, "Respond in clear, simple English.")

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

    unsupported_msg = {
        "hindi": "मैं अभी केवल AC, washing machine और microwave oven के लिए support कर सकता हूँ.",
        "hinglish": "Main abhi sirf AC, washing machine aur microwave oven ke liye support kar sakta hoon.",
        "english": "I currently support only ACs, washing machines, and microwave ovens.",
    }.get(language, "I currently support only ACs, washing machines, and microwave ovens.")

    return f"""You are a helpful, friendly customer support voice agent for ElectroServ, an electronics company.
You specialize in: Air Conditioners (AC), Washing Machines, and Microwave Ovens.

## Current Context:
- Product: {product_display}
- Detected Issue: {intent or "Not yet identified"}
- Language Mode: {language}

## Language Rule:
{lang_instruction}

## Rules:
1. Never make up product information or model numbers not provided.
2. Always use the knowledge base context below when available.
3. If the product is not an AC, washing machine, or microwave, say: "{unsupported_msg}"
4. Keep responses short and conversational, 2 to 4 sentences max for voice.
5. If the issue seems unresolved after 2 exchanges, suggest creating a service ticket.
6. Ask for customer name and phone number only when creating a ticket.
7. Be empathetic because customers are frustrated when appliances break.
{knowledge_context}
"""
