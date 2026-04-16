# ARCHITECTURE.md

## High-Level Architecture
- **Client Server Separation:** A vanilla HTML/JS frontend interacts with a FastAPI backend asynchronously.
- **Local Compute:** Operations are local and rely on the filesystem, but heavily orchestrate external AI services.

## Application Flow
1. **Intake:** The SPA handles image selection and implements progressive client-side compression before initiating an upload to `/api/process`. Max allowed payload is 10 MB.
2. **Job Orchestration:** Backend acknowledges upload with a `job_id` and spawns a background asyncio task to execute the pipeline. Frontend iteratively polls `/api/status/{job_id}`.
3. **Data Extraction:** Document is sent to Mistral OCR. Received markdown is chunked and analyzed via local deterministic regex (`field_extractor.py`) to detect layout primitives (e.g., labels, checkboxes).
4. **Knowledge Retrieval (RAG):** Local civic dataset is loaded. Guideline context is dynamically appended per page and per field using a hybrid strategy (0.7 semantic + 0.3 keyword scoring).
5. **AI Synthesis:** Extracted text and retrieved guidelines are bundled and sent to Mistral LLM to generate plain-language explanations. Validation rules (`validators.py`) overlay deterministic warnings.
6. **Audio Output:** Final step triggers asynchronous MP3 generation via ElevenLabs (or gTTS) mapped to specific data fields or full page summaries.
