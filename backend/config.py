from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    groq_api_key: str = "your_groq_api_key_here"
    database_url: str = "postgresql://postgres:password@localhost:5432/voice_support_db"
    app_env: str = "development"
    cors_origins: str = "http://localhost:3000"

    # Groq model config
    whisper_model: str = "whisper-large-v3"
    llm_model: str = "llama-3.3-70b-versatile"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",")]


@lru_cache()
def get_settings() -> Settings:
    return Settings()
