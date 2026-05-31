import io
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
def transcribe_audio(audio_bytes: bytes, filename: str = "audio.webm") -> dict:
    """
    Send raw audio bytes to Groq Whisper.
    Returns { transcript, language, duration }
    """
    client = get_groq_client()
    audio_file = io.BytesIO(audio_bytes)
    audio_file.name = filename

    transcription = client.audio.transcriptions.create(
        file=(filename, audio_file, "audio/webm"),
        model=settings.whisper_model,
        response_format="verbose_json",
    )

    return {
        "transcript": transcription.text.strip(),
        "language": getattr(transcription, "language", "en"),
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
