# CONVENTIONS.md

## Data Models & Validation
- **Pydantic Validation**: All structured API and internal responses follow Pydantic schema validation as defined in `backend/schema.py`. It guarantees data shape integrity between the internal LLM/RAG/OCR processes and the API outputs.

## Style and Typings
- **Type Hints**: Standard Python type hints (PEP 484) are expected throughout the backend codebase to support fast Pydantic schema generation and readability.
- **Asynchrony**: All major tasks invoked within `main.py` MUST support `asyncio` or wrap synchronous external I/O within asynchronous functions (e.g., ElevenLabs / gTTS HTTP calls) to prevent blocking the Uvicorn event loop.

## API Response Shapes
- **Response Shape**: `/api/status/{job_id}` consistently returns data shaped around a `status` key corresponding to standard application states (`pending`, `processing`, `completed`, `failed`). Completion appends a `result` payload mirroring `schema.PageOutput`.
- **Error Responses**: Validation boundaries naturally return HTTP 422 Unprocessable Entity for schema violations. Explicit process aborts (like file size limits) yield specific HTTP 4xx definitions inside FastAPI.
