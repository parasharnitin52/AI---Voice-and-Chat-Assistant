"""
Text-to-Speech helper using Microsoft Edge TTS (edge-tts).
Provides high-quality neural voices with multi-language support.
"""
import io
import asyncio
import edge_tts

# Default voices per language
VOICE_MAP = {
    "english": "en-IN-NeerjaNeural",    # Indian English female
    "hindi": "hi-IN-SwaraNeural",       # Hindi female
    "hinglish": "hi-IN-SwaraNeural",    # Use Hindi voice for Hinglish so it reads romanized Hindi naturally
}


async def _synthesize_async(text: str, language: str = "english") -> bytes:
    """Generate speech audio bytes using edge-tts (async)."""
    voice = VOICE_MAP.get(language.lower(), VOICE_MAP["english"])

    communicate = edge_tts.Communicate(text, voice)
    audio_chunks: list[bytes] = []

    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_chunks.append(chunk["data"])

    return b"".join(audio_chunks)


def synthesize(text: str, language: str = "english") -> bytes:
    """Synchronous wrapper around the async edge-tts synthesizer.

    Args:
        text: The text to be spoken.
        language: One of 'english', 'hindi', 'hinglish'.

    Returns:
        MP3 audio bytes ready to be streamed back to the client.
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        # We're inside an already-running event loop (e.g. FastAPI with uvicorn).
        # Create a new thread to run the coroutine.
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as pool:
            future = pool.submit(asyncio.run, _synthesize_async(text, language))
            return future.result()
    else:
        return asyncio.run(_synthesize_async(text, language))
