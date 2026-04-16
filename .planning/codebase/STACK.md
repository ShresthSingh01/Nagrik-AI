# STACK.md

## Languages & Frameworks
- **Backend:** Python 3, using FastAPI as the web framework and Uvicorn as the ASGI server.
- **Frontend:** Vanilla HTML5, CSS3, and JavaScript (ES6). No complex build steps or frameworks (like React or Vue) are used.

## Libraries & Dependencies
- `fastapi` and `uvicorn`: Web server and routing.
- `python-multipart`: Handling file uploads.
- `requests`: Making network calls to external APIs.
- `pydantic`: Data validation and schema definition.
- `gTTS`: Google Text-to-Speech library used as a fallback.
- `python-dotenv`: Environment variable management.
- `numpy`: Used for numeric operations (e.g., embeddings math).

## Storage & Persistence
- **Backend:** Completely file-system based. Local JSON job files are stored in `output/jobs/*.json` and audio files in `output/audio/*.mp3`.
- **Frontend:** Standard browser `localStorage` is used to persist user history and settings (like language and simplification level). No remote database exists.
