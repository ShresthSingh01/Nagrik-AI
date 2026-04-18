import os
import requests
import re
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
MISTRAL_BASE_URL = os.getenv("MISTRAL_BASE_URL", "https://api.mistral.ai/v1")
MISTRAL_OCR_MODEL = os.getenv("MISTRAL_OCR_MODEL", "mistral-ocr-latest")

def test_api():
    print(f"Testing Mistral API at {MISTRAL_BASE_URL}...")
    headers = {"Authorization": f"Bearer {MISTRAL_API_KEY}"}
    try:
        resp = requests.get(f"{MISTRAL_BASE_URL}/models", headers=headers)
        print(f"Models check status: {resp.status_code}")
        if resp.status_code != 200:
            print(f"Error: {resp.text}")
            return False
        
        models = [m["id"] for m in resp.json().get("data", [])]
        print(f"Found model {MISTRAL_OCR_MODEL}: {MISTRAL_OCR_MODEL in models}")
        return True
    except Exception as e:
        print(f"Exception: {e}")
        return False

if __name__ == "__main__":
    if not MISTRAL_API_KEY:
        print("MISTRAL_API_KEY is missing!")
    else:
        test_api()
