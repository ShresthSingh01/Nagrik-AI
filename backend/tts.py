from __future__ import annotations  # Future compatibility ke liye, type hints ko better banata hai

import requests  # API calls karne ke liye (internet pe request bhejne ke liye)
import logging  # Logging system (info, error, warning print karne ke liye structured way me)
from gtts import gTTS  # Google Text-to-Speech fallback ke liye
from .config import settings  # Config file se settings (jaise API key) import kar rahe hain

logger = logging.getLogger(__name__)  # Logger object bana rahe hain current file ke liye

# Enhanced Voice Discovery (Self-Healing)
_VOICE_CACHE = {}  # Cache dictionary jisme voice IDs store honge taaki baar-baar API call na karna pade

def _resolve_voice_id(lang_code: str, api_key: str) -> str:
    """Finds the best available voice in the user's account by name fuzzy matching."""
    cache_key = f"voice_{lang_code}"  # Cache key banaya language ke basis pe
    if cache_key in _VOICE_CACHE:  # Agar already cache me hai
        return _VOICE_CACHE[cache_key]  # Direct wahi voice ID return kar do

    try:
        url = "https://api.elevenlabs.io/v1/voices"  # ElevenLabs voices API endpoint
        headers = {"xi-api-key": api_key}  # API key header me bhej rahe hain
        response = requests.get(url, headers=headers, timeout=10)  # GET request bhej rahe hain
        voices = response.json().get("voices", [])  # JSON se voices list nikaal rahe hain
        if not voices:  # Agar koi voice nahi mila
            return None  # None return kar do

        # Filter for 'premade' voices only (Professional/Library voices are often paid-only)
        premade_voices = [v for v in voices if v.get("category") == "premade"]  # Sirf premade (free) voices filter kar rahe hain
        if not premade_voices:  # Agar premade voices nahi mile
            # If no premade, use whatever they have
            premade_voices = voices  # Jo bhi available hai use kar lo

        # Preference Order (by Name)
        if "hi" in lang_code.lower():  # Agar Hindi language hai
            # Liam and Adam are premade and support Hindi Multilingual v2
            targets = ["Liam", "Adam", "Rachel", "Sarah"]  # Preferred voices list
        else:
            targets = ["Rachel", "Sarah", "Alice", "Emily"]  # English ke liye preferred voices

        # 1. Look for targets in premade list
        for target in targets:  # Preferred names loop
            for v in premade_voices:  # Har premade voice check karo
                if target.lower() in v["name"].lower():  # Agar name match karta hai
                    print(f"[Nagrik] Auto-discovered premade voice for '{lang_code}': {v['name']} ({v['voice_id']})")  # Debug print
                    _VOICE_CACHE[cache_key] = v["voice_id"]  # Cache me store kar do
                    return v["voice_id"]  # Voice ID return kar do

        # 2. Fallback to first available premade
        fallback_id = premade_voices[0]["voice_id"]  # First available voice ko fallback bana lo
        print(f"[Nagrik] Warning: Preferred premade voice not found. Using fallback: {premade_voices[0]['name']}")  # Warning print
        _VOICE_CACHE[cache_key] = fallback_id  # Cache me store kar do
        return fallback_id  # Fallback voice return karo

    except Exception as e:  # Agar koi error aata hai
        print(f"[Nagrik] Voice discovery failed: {e}")  # Error print karo
        return None  # None return karo

def text_to_speech(text: str, output_path: str, lang: str = "en") -> str:
    clean_text = (text or "").strip()  # Text clean kar rahe hain (None handle + spaces remove)
    if not clean_text:  # Agar text empty ho
        clean_text = "No explanation available."  # Default text set kar do
        
    # Check if ElevenLabs is configured natively
    if settings.elevenlabs_api_key:  # Agar ElevenLabs API key available hai
        try:
            # Dynamic voice resolution (brutal fix for 404s)
            voice_id = _resolve_voice_id(lang, settings.elevenlabs_api_key)  # Voice ID auto find karo
            if not voice_id:  # Agar voice ID nahi mila
                raise Exception("No voices available in account")  # Exception throw karo
            
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"  # TTS API endpoint
            headers = {
                "Accept": "audio/mpeg",  # Output audio format
                "Content-Type": "application/json",  # JSON payload bhej rahe hain
                "xi-api-key": settings.elevenlabs_api_key  # API key
            }
            
            payload = {
                "text": clean_text,  # Jo text speak karna hai
                "model_id": "eleven_multilingual_v2",  # Multilingual model use kar rahe hain
                "voice_settings": {
                    "stability": 0.5,  # Voice stability (smoothness)
                    "similarity_boost": 0.75  # Voice similarity boost
                }
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)  # POST request bhej rahe hain
            if response.status_code == 200:  # Agar success mila
                with open(output_path, 'wb') as f:  # File open karo write mode me (binary)
                    f.write(response.content)  # Audio content save karo
                return output_path  # Output path return karo
            else:
                logger.warning(f"ElevenLabs API Error {response.status_code}: {response.text}")  # Warning log karo
                # Fallthrough to gTTS
        except Exception as e:
            logger.error(f"ElevenLabs Request Failed: {e}")  # Error log karo
            # Fallthrough to gTTS

    # Fallback: gTTS
    logger.info(f"Using gTTS fallback for lang '{lang}'")  # Info log karo ki fallback use ho raha hai
    tts = gTTS(text=clean_text, lang=lang)  # gTTS object create karo
    tts.save(output_path)  # Audio file save karo
    return output_path  # Output path return karo
