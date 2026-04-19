from __future__ import annotations

import requests
import logging
from gtts import gTTS
from .config import settings

logger = logging.getLogger(__name__)

# Enhanced Voice Discovery (Self-Healing)
_VOICE_CACHE = {}

def _resolve_voice_id(lang_code: str, api_key: str) -> str:
    """Finds the best available voice in the user's account by name fuzzy matching."""

    cache_key = f"voice_{lang_code}"
    if cache_key in _VOICE_CACHE:
        return _VOICE_CACHE[cache_key]

    try:
        url = "https://api.elevenlabs.io/v1/voices"
        headers = {"xi-api-key": api_key}
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code in [401, 403]:
            logger.error(f"[Nagrik] ElevenLabs Authorization Failed ({response.status_code}): {response.text}")
            return None

        if not response.ok:
            logger.warning(f"[Nagrik] ElevenLabs Voice List failed: {response.status_code}")
            return None

        voices = response.json().get("voices", [])
        if not voices:
            return None

        # Filter for 'premade' voices only (Professional/Library voices are often paid-only)
        premade_voices = [v for v in voices if v.get("category") == "premade"]
        if not premade_voices:
            # If no premade, use whatever they have
            premade_voices = voices

        # Preference Order (by Name)
        if "hi" in lang_code.lower():
            targets = ["Liam", "Adam", "Rachel", "Sarah"]
        else:
            targets = ["Rachel", "Sarah", "Alice", "Emily"]

        # 1. Look for targets in premade list
        for target in targets:
            for v in premade_voices:
                if target.lower() in v["name"].lower():
                    print(f"[Nagrik] Auto-discovered premade voice for '{lang_code}': {v['name']} ({v['voice_id']})")
                    _VOICE_CACHE[cache_key] = v["voice_id"]
                    return v["voice_id"]

        # 2. Fallback to first available premade
        if not premade_voices:
            return None

        fallback_id = premade_voices[0]["voice_id"]
        print(f"[Nagrik] Warning: Preferred premade voice not found. Using fallback: {premade_voices[0]['name']}")
        _VOICE_CACHE[cache_key] = fallback_id
        return fallback_id

    except Exception as e:
        print(f"[Nagrik] Voice discovery failed: {e}")
        return None

def text_to_speech(text: str, output_path: str, lang: str = "en") -> str:
    clean_text = (text or "").strip()
    if not clean_text:
        clean_text = "No explanation available."
        
    # Check if ElevenLabs is configured
    if settings.elevenlabs_api_key:
        try:
            # Dynamic voice resolution
            voice_id = _resolve_voice_id(lang, settings.elevenlabs_api_key)
            if not voice_id:
                # Fall through to gTTS immediately if discovery failed
                raise Exception("No active voices found or API blocked")
            
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": settings.elevenlabs_api_key
            }
            
            payload = {
                "text": clean_text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75
                }
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                return output_path
            
            # Specific check for errors
            if response.status_code != 200:
                logger.error(f"ElevenLabs API Error {response.status_code}: {response.text}")
                # Fall through to gTTS

        except Exception as e:
            logger.error(f"ElevenLabs Request Failed: {e}")
            # Fallthrough to gTTS

    # Fallback: gTTS
    logger.info(f"Using gTTS fallback for lang '{lang}'")
    try:
        tts = gTTS(text=clean_text, lang=lang)
        tts.save(output_path)
    except Exception as e:
        logger.error(f"gTTS also failed: {e}")
        # Create an empty file to avoid breaking the UI paths, or raise
        with open(output_path, 'wb') as f:
            f.write(b"") 
    return output_path
