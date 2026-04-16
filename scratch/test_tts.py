import sys
import os
from pathlib import Path

# Add the project root to sys.path to import from backend
sys.path.append(str(Path(__file__).resolve().parent.parent))

from backend.tts import text_to_speech

def test_hindi_tts():
    print("---[ Nagrik TTS Test ]---")
    output_path = "output/audio/test_hindi.mp3"
    test_text = "नमस्ते, यह नागरिक सहायक का एक परीक्षण है।" # Namaste, this is a test of Nagrik Assistant
    
    # Ensure audio dir exists
    os.makedirs("output/audio", exist_ok=True)
    
    print(f"Testing Hindi TTS with ElevenLabs dynamic resolution...")
    result = text_to_speech(test_text, output_path, lang="hi")
    
    if result and os.path.exists(result):
        size = os.path.getsize(result)
        print(f"SUCCESS: Audio generated at {result} (Size: {size} bytes)")
    else:
        print("FAILURE: Audio file not created.")

if __name__ == "__main__":
    test_hindi_tts()
