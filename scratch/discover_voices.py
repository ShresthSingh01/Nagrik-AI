import requests
import os
import json
from dotenv import load_dotenv

def discover_voices():
    load_dotenv()
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        print("ERROR: No ELEVENLABS_API_KEY found in .env")
        return

    url = "https://api.elevenlabs.io/v1/voices"
    headers = {"xi-api-key": api_key}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"ERROR: {response.status_code} - {response.text}")
            return
            
        data = response.json()
        voices = data.get("voices", [])
        print(f"Found {len(voices)} available voices:")
        for v in voices:
            print(f"- {v['name']} ({v['voice_id']}) | Category: {v['category']}")
            
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    discover_voices()
