# Local Language Civic Document Translator MVP

A beginner-friendly full stack MVP using:
- Plain HTML / CSS / JavaScript frontend
- Python FastAPI backend
- Mistral OCR for document extraction
- PageIndex-style tree indexing for page-aware retrieval
- Local civic knowledge base for grounded explanations
- Optional Mistral chat completion for simplification
- gTTS for audio output

## Run

### Windows (recommended)

From project root:

```powershell
./scripts/start_server.ps1
```

This script will:
1. Create `.venv` if missing
2. Install/upgrade dependencies from `backend/requirements.txt`
3. Create `.env` from `.env.example` if missing
4. Start FastAPI with Uvicorn

Alternative launcher:

```bat
start-server.bat
```

Useful options:

```powershell
# Skip dependency install
./scripts/start_server.ps1 -SkipInstall

# Disable reload mode
./scripts/start_server.ps1 -NoReload

# Custom port
./scripts/start_server.ps1 -Port 8080

# Custom host binding
./scripts/start_server.ps1 -BindHost 0.0.0.0 -Port 8000
```

Open `http://127.0.0.1:8000`.

### Manual setup (all platforms)

```bash
python -m venv .venv

# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# macOS/Linux
# source .venv/bin/activate

pip install -r backend/requirements.txt
cp .env.example .env
python -m uvicorn backend.main:app --reload
```

## Notes
- Upload a PDF or image.
- The app uploads the file to Mistral Files API with `purpose=ocr`, then calls OCR.
- The OCR response is turned into a page-aware tree index, then relevant civic guidance is retrieved and simplified.
- If the chat model is not configured, the app still returns a deterministic fallback explanation.

## Environment

Create a `.env` file in the project root with values like:

```env
MISTRAL_API_KEY=your_key_here
MISTRAL_BASE_URL=https://api.mistral.ai/v1
MISTRAL_OCR_MODEL=mistral-ocr-latest
MISTRAL_CHAT_MODEL=mistral-small-latest
MAX_CONTEXT_NODES=3
MAX_GUIDELINE_HITS=3
TTS_LANGUAGE=en
ELEVENLABS_API_KEY=
```
