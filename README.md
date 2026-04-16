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

```bash
cd civic_translator_mvp
python -m venv .venv
# activate your venv
pip install -r backend/requirements.txt

copy .env.example .env   # optional, then fill in your key

# or set it directly in your shell
set MISTRAL_API_KEY=your_key   # Windows CMD
# $env:MISTRAL_API_KEY="your_key"  # PowerShell
# export MISTRAL_API_KEY=your_key  # macOS/Linux

uvicorn backend.main:app --reload
```

Open `http://127.0.0.1:8000`.

## Notes
- Upload a PDF or image.
- The app uploads the file to Mistral Files API with `purpose=ocr`, then calls OCR.
- The OCR response is turned into a page-aware tree index, then relevant civic guidance is retrieved and simplified.
- If the chat model is not configured, the app still returns a deterministic fallback explanation.

## Environment

Create a `.env` file in the project root with values like:

```env
MISTRAL_API_KEY=your_key_here
MISTRAL_CHAT_MODEL=mistral-large-latest
```
