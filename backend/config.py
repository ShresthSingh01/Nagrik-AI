from dataclasses import dataclass
import os

from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    mistral_api_key: str = os.getenv("MISTRAL_API_KEY", "").strip()
    mistral_base_url: str = os.getenv("MISTRAL_BASE_URL", "https://api.mistral.ai/v1").strip()
    mistral_ocr_model: str = os.getenv("MISTRAL_OCR_MODEL", "mistral-ocr-latest").strip()
    mistral_chat_model: str = os.getenv("MISTRAL_CHAT_MODEL", "mistral-large-latest").strip()
    elevenlabs_api_key: str = os.getenv("ELEVENLABS_API_KEY", "").strip()
    max_context_nodes: int = int(os.getenv("MAX_CONTEXT_NODES", "3"))
    max_guideline_hits: int = int(os.getenv("MAX_GUIDELINE_HITS", "3"))
    tts_language: str = os.getenv("TTS_LANGUAGE", "en").strip()

settings = Settings()
