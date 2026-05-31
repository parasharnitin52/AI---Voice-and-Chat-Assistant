import io
import re
from groq import Groq
from config import get_settings

settings = get_settings()

# Singleton Groq client
_client: Groq | None = None


def get_groq_client() -> Groq:
    global _client
    if _client is None:
        _client = Groq(api_key=settings.groq_api_key)
    return _client


# ─────────────────────────────────────────────
#  Speech-to-Text  (Groq Whisper)
# ─────────────────────────────────────────────
DISALLOWED_TRANSCRIPT_SCRIPT_RE = re.compile(
    r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF"
    r"\u0980-\u0C7F\u0D00-\u0D7F]"
)


def normalize_transcript_script(
    transcript: str,
    language_hint: str | None = None,
    detected_language: str | None = None,
) -> str:
    """
    Keep transcripts in Roman letters or Hindi Devanagari.
    Whisper can sometimes return Hindi/Hinglish in Urdu or another Indic script.
    """
    if not transcript or not DISALLOWED_TRANSCRIPT_SCRIPT_RE.search(transcript):
        return transcript

    normalized_hint = (language_hint or detected_language or "").strip().lower()
    target_script = "Hindi Devanagari" if normalized_hint in {"hi", "hindi", "ur", "urdu"} else "Roman English alphabet"
    if not normalized_hint:
        target_script = "Hindi Devanagari if the sentence is Hindi, otherwise Roman English alphabet"

    client = get_groq_client()
    response = client.chat.completions.create(
        model=settings.llm_model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You rewrite speech transcripts only. Convert the input into "
                    f"{target_script}. Never use Urdu, Arabic, Persian, Tamil, "
                    "Bengali, Telugu, Kannada, Malayalam, or any script other "
                    "than Roman English letters or Hindi Devanagari. Preserve the "
                    "speaker's meaning. Do not answer the user. Return only the "
                    "rewritten transcript."
                ),
            },
            {"role": "user", "content": transcript},
        ],
        temperature=0,
        max_tokens=160,
    )
    cleaned = response.choices[0].message.content.strip().strip('"')
    return cleaned or transcript


def transcribe_audio(
    audio_bytes: bytes,
    filename: str = "audio.webm",
    content_type: str = "audio/webm",
    language_hint: str | None = None,
) -> dict:
    """
    Send raw audio bytes to Groq Whisper.
    Returns { transcript, language, duration }
    """
    client = get_groq_client()
    audio_file = io.BytesIO(audio_bytes)
    audio_file.name = filename

    request_args = {
        "file": (filename, audio_file, content_type or "audio/webm"),
        "model": settings.whisper_model,
        "response_format": "verbose_json",
        "prompt": (
            "Transcribe exactly what the speaker says. Preserve Hindi in "
            "Devanagari when spoken in Hindi. Preserve Hinglish as Romanized "
            "Hindi mixed with English. Use only Hindi Devanagari or Roman "
            "English letters. Never use Urdu, Arabic, or Persian script. "
            "Do not translate to English."
        ),
    }

    if language_hint:
        normalized_hint = language_hint.strip().lower()
        if normalized_hint in {"hi", "hindi", "hinglish"}:
            request_args["language"] = "hi"
        elif normalized_hint in {"en", "english"}:
            request_args["language"] = "en"

    transcription = client.audio.transcriptions.create(**request_args)

    detected_language = getattr(transcription, "language", "en")
    transcript = normalize_transcript_script(
        transcription.text.strip(),
        language_hint=language_hint,
        detected_language=detected_language,
    )

    return {
        "transcript": transcript,
        "language": detected_language,
        "duration": getattr(transcription, "duration", None),
    }


# ─────────────────────────────────────────────
#  LLM Chat  (Groq LLaMA 3.3 70B)
# ─────────────────────────────────────────────
def chat_completion(messages: list[dict], system_prompt: str) -> str:
    """
    Call Groq LLaMA with a system prompt + message history.
    Returns the assistant's reply text.
    """
    client = get_groq_client()

    full_messages = [{"role": "system", "content": system_prompt}] + messages

    response = client.chat.completions.create(
        model=settings.llm_model,
        messages=full_messages,
        temperature=0.4,
        max_tokens=512,
        top_p=0.9,
    )

    return response.choices[0].message.content.strip()
