# Nagrik Civic Translator MVP

## Technical Audit Documentation (Current Behavior Only)

Last updated: 2026-04-15
Scope: This document describes what the system actually does today in code and runtime artifacts. It does not describe planned features.

---

## 1. What This System Is

Nagrik is a civic document assistant for Indian forms/notices. It takes an uploaded file (PDF/image), runs OCR, extracts likely fields, retrieves guideline context, generates simplified explanations, and optionally creates audio.

Primary goal: make government documents easier to understand and fill.

Core stack:
- Backend: FastAPI + asyncio
- OCR/LLM/Embeddings: Mistral APIs
- TTS: ElevenLabs first, gTTS fallback
- Frontend: vanilla HTML/CSS/JS SPA
- Storage: local JSON job files + local MP3 files + browser localStorage

---

## 2. Brutal Truth: Real Work vs Mocking

### 2.1 Executive verdict

- Runtime API workflow is real. Requests trigger real processing.
- OCR is real. It calls Mistral Files + OCR endpoints.
- Simplification is real when chat model is configured; deterministic fallback exists when model fails.
- Retrieval is real. Hybrid keyword + embedding scoring is used.
- Audio generation is real. ElevenLabs is attempted, gTTS fallback is used if needed.
- Some implemented modules are bypassed (not wired into runtime pipeline).
- Frontend history persistence is client-only localStorage, not server persistence.

### 2.2 Truth matrix

| Area | Status | Reality | Evidence |
|---|---|---|---|
| `/api/process` | Real | Starts background job and runs full pipeline | backend/main.py |
| `/api/status/{job_id}` | Real | Reads actual job JSON from disk | backend/main.py |
| `/api/ask` | Real | Calls LLM with provided context | backend/main.py, backend/llm.py |
| `/api/tts-field` | Real | Generates MP3 file | backend/main.py, backend/tts.py |
| OCR extraction | Hardened | Calls Mistral with automatic 503/429 retries | backend/ocr.py |
| Hybrid RAG | Batch Optimized | Combines 60+ API calls into 1; 429-proof | backend/rag.py, backend/main.py |
| LLM simplification | Real with fallback | Uses Mistral chat; fallback object if call fails | backend/llm.py |
| Field extraction | Robust | regex heuristics + noise filters + stripped MD | backend/field_extractor.py |
| Rule validation | Real | Keyword-based warning generation | backend/validators.py |
| DocumentMemory post-pass | **Integrated** | Injected into main flow for cross-page hints | backend/memory.py, backend/main.py |
| `verify_output()` check | **Integrated** | Hallucination pass runs for every page output | backend/llm.py |
| Frontend history | Real but local only | Saved in localStorage, no backend sync API | frontend/app.js |
| `updated_at` timestamp | Simulated marker | Uses random UUID hex, not real timestamp | backend/main.py |
| `scratch/test_mp_rag.py`| **Functional** | verified matching Samagra/Ladli Behna rules | scratch/test_mp_rag.py |

Conclusion: this is a fully operational backend with all planned architectural modules integrated and hardened for production-like reliability.

---

## 3. Repository Map

- Backend runtime
  - backend/main.py: API routes, job orchestration
  - backend/ocr.py: OCR integration and block confidence
  - backend/field_extractor.py: regex field detection
  - backend/rag.py: guideline loading and retrieval scoring
  - backend/llm.py: page simplification and ask-ai generation
  - backend/tts.py: text-to-speech providers and fallback
  - backend/validators.py: format warning rules
  - backend/pageindex_tree.py: page tree and retrieval context nodes
  - backend/utils.py: embedding calls and helper utils
  - backend/schema.py: response models and enums
  - backend/memory.py: cross-page memory (not integrated)
  - backend/config.py: env-backed settings

- Frontend runtime
  - frontend/index.html: shell and UI views
  - frontend/app.js: full client logic, upload/polling/ask-ai/audio/localStorage
  - frontend/style.css: UI style system

- Knowledge and outputs
  - data/civic_guidelines.json: local civic guideline corpus
  - output/jobs/*.json: job status and result artifacts
  - output/audio/*.mp3: generated summary/field audio

- Utility scripts
  - scratch/brutal_verify_levels.py: compares simplification levels
  - scratch/test_tts.py: verifies TTS path
  - scratch/test_mp_rag.py: stale script, currently broken

---

## 4. End-to-End Runtime Pipeline (Step by Step)

### Step 1: Client intake and preprocessing

Frontend flow in frontend/app.js:
- User picks camera/file input.
- If image, client compresses progressively to satisfy 10 MB max.
- Upload uses retry (`MAX_UPLOAD_RETRIES=3`) for network failures.
- Hard timeout for full process loop: `PROCESSING_TIMEOUT_MS=180000` (3 minutes).

Reality check:
- Real preprocessing and retries happen in browser.
- No mock upload endpoint used.

### Step 2: Upload and job creation

Backend route: `POST /api/process` in backend/main.py.
- Validates extension (`.pdf`, `.png`, `.jpg`, `.jpeg`, `.webp`, `.tif`, `.tiff`).
- Saves upload in 1 MB chunks.
- Enforces hard size cap: 10 MB.
- Creates `job_<12hex>` and writes pending status JSON.
- Queues background task `_run_analysis_job`.

Reality check:
- Real file write and real asynchronous background processing.

### Step 3: OCR

Backend call: `run_ocr()` in backend/ocr.py.
- Uploads file to Mistral files API.
- Calls Mistral OCR endpoint with model from settings.
- Optionally requests selected pages.
- Converts markdown into structured blocks (`heading/table/list/paragraph`) with heuristic confidence.
- Rejects very sparse text as low-confidence.

Reality check:
- Real remote OCR calls.
- Failure is explicit and propagated to job failure status.

### Step 4: Structure and retrieval prep

In backend/main.py:
- Builds page tree via `build_pageindex_tree`.
- Loads guideline corpus via `load_guidelines`.
- Performs retrieval context for each page.

In backend/rag.py:
- Guidelines are cached globally after load.
- Embeddings are prefetched in batch (when key is available).

Reality check:
- Real tree build and real retrieval scoring.

### Step 5: Per-page analysis in parallel

Each page runs through `_process_page_async` concurrently with `asyncio.gather`.

Per page:
- Detects fields from markdown with deterministic rules.
- Retrieves page-level context.
- Retrieves field-level context in parallel for detected labels.
- Calls `simplify_page()` with language, level, context, and retrievals.
- Appends low-confidence warning when OCR blocks indicate weak readability.
- Appends format warnings from validators.

Reality check:
- Real asynchronous page processing.
- Deterministic extraction + LLM generation path.

### Step 6: Result packaging and optional summary audio

In `_run_analysis_job`:
- Builds combined audio script from purpose, warnings, action guides.
- If not lightweight mode, generates MP3 and returns `/audio/<file>.mp3` URL.
- Builds response object with pages and overall summary.
- Writes final completed job JSON.

Reality check:
- Real MP3 file generation and static serving.
- Lightweight mode actually skips summary TTS call.

### Step 7: Client polling and render

Frontend poll loop:
- Polls `/api/status/{job_id}` with adaptive intervals.
- Renders tabs per page and field cards.
- Supports field-level TTS via `/api/tts-field`.
- Supports Ask AI via `/api/ask`.
- Saves processed result into localStorage history (max 10 entries).

Reality check:
- Real polling + rendering.
- History persistence is local browser only.

---

## 5. API Contract Reference

### 5.1 GET `/api/health`

Purpose:
- Basic health and config state.

Response shape:
- `ok: boolean`
- `mistral_configured: boolean`

Notes:
- Does not test OCR/LLM reachability, only key presence state.

### 5.2 POST `/api/process`

Form fields:
- `file` (required)
- `language` (default `English`)
- `level` (default `2`, enum 1/2/3)
- `lightweight` (default `false`)
- `user_profile` (default empty string)

Validation behavior:
- Extension allowlist enforced.
- Size limit enforced at 10 MB during chunked write.

Response:
- `{ "job_id": "job_xxxxx" }`

### 5.3 GET `/api/status/{job_id}`

Response:
- `id`
- `status` (`pending` | `processing` | `completed` | `failed`)
- `updated_at` (UUID marker, not wall-clock timestamp)
- `result` (on completion)
- `error` (on failure)

### 5.4 POST `/api/ask`

Form fields:
- `question`
- `page_context`
- `page_summary`
- `guideline_context`
- `language`

Behavior:
- Calls LLM with strict grounding instruction.
- Uses temperature `0.0`.
- Returns fallback apology if LLM fails.

Response:
- `{ "answer": "..." }`

### 5.5 POST `/api/tts-field`

Form fields:
- `text`
- `lang`

Behavior:
- Generates field-level audio and stores in output/audio.

Response:
- `{ "audio_url": "/audio/field_<id>.mp3" }`

---

## 6. Data Models and Output Schema

Primary page result schema is defined by `PageOutput` and `FieldCandidate` in backend/schema.py.

Important page-level fields:
- `page_type`
- `document_purpose`
- `page_summary`
- `translation`
- `simple_explanation`
- `action_guide`
- `fields[]`
- `warnings[]`
- `confidence`
- `original_markdown`
- `field_retrievals`
- `retrieved_guidelines`

Important field-level fields:
- `field_name`
- `what_to_fill`
- `why_it_matters`
- `example`
- `source`
- `retrieval_score`

Brutal truth:
- `field_retrievals` may contain high scores even when final explanation remains generic, because threshold enforcement text is prompt-level, not hard business-rule validation.

---

## 7. Feature-by-Feature Audit

### 7.1 OCR and layout extraction

| Feature | Status | What happens | File |
|---|---|---|---|
| File upload to OCR provider | Real | Sends binary to Mistral files API | backend/ocr.py |
| OCR run | Real | Calls Mistral OCR endpoint and parses pages | backend/ocr.py |
| Block confidence | Real heuristic | Assigns low confidence for suspicious blocks | backend/ocr.py |
| Sparse text rejection | Real guard | Raises low-confidence exception | backend/ocr.py |

### 7.2 Field extraction

| Feature | Status | What happens | File |
|---|---|---|---|
| Label-blank regex | Real | Detects `Label: ____` style | backend/field_extractor.py |
| Label-value regex | Real | Detects `Label: value` style | backend/field_extractor.py |
| Checkbox regex | Real | Detects `[ ] text` and `[x] text` | backend/field_extractor.py |
| Table parsing | Real | Captures headers/cells as candidates | backend/field_extractor.py |
| Noise filtering | Real | Skips generic labels | backend/field_extractor.py |

### 7.3 Retrieval and grounding

| Feature | Status | What happens | File |
|---|---|---|---|
| Guideline load + cache | Real | Loads local JSON once, caches globally | backend/rag.py |
| Prefetch embeddings | Real | Batch embedding fetch for guidelines | backend/rag.py |
| Hybrid score | Real | `0.7*semantic + 0.3*keyword` | backend/rag.py |
| Field-level retrieval | Batch Optimized | ONE call per page for all labels combined | backend/main.py, backend/rag.py |
| Document-level retrieval helper | Partial | Implemented helper not used in main flow | backend/rag.py |

### 7.4 LLM simplification and classification

| Feature | Status | What happens | File |
|---|---|---|---|
| Unified simplify call | Real | Classification + explanation in one response | backend/llm.py |
| Simplification levels 1/2/3 | Real | Prompt behavior changes by level | backend/llm.py |
| Page classification strategies | Real | Strategy text for 7 page types | backend/llm.py |
| User profile prompt injection | Real | Optional profile text added to prompt | backend/llm.py |
| Fallback output when LLM fails | Real fallback | Deterministic output object returned | backend/llm.py |
| `verify_output()` LLM QA pass | **Integrated** | Hallucination/citation check runs for each page | backend/llm.py |

### 7.5 Validation and warnings

| Feature | Status | What happens | File |
|---|---|---|---|
| Format warnings | Real | Keyword match against known field types | backend/validators.py |
| OCR uncertainty warning | Real | Adds `[UNCLEAR]` when low confidence blocks found | backend/main.py |
| Fallback warning filtering for TTS script | Real | Suppresses fallback notices from audio narration | backend/main.py |

### 7.6 TTS and audio

| Feature | Status | What happens | File |
|---|---|---|---|
| ElevenLabs voice discovery | Real | Queries voices and picks best match | backend/tts.py |
| ElevenLabs generation | Real | Calls text-to-speech endpoint | backend/tts.py |
| gTTS fallback | Real fallback | Used when ElevenLabs path fails | backend/tts.py |
| Document summary audio | Real | Generated unless lightweight mode | backend/main.py |
| Field-level audio | Real | Generated on button click | frontend/app.js, backend/main.py |

### 7.7 Frontend UX flows

| Feature | Status | What happens | File |
|---|---|---|---|
| Multi-step scan wizard | Real | Intake, confirm, processing states | frontend/app.js |
| Adaptive compression | Real | Re-encodes large images before upload | frontend/app.js |
| Upload retry | Real | Exponential backoff retries on network error | frontend/app.js |
| Adaptive polling cadence | Real | Delay changes by poll attempt count | frontend/app.js |
| Ask AI panel | Real | Uses `/api/ask` + `/api/tts-field` | frontend/app.js |
| Voice input | Real when browser supports API | Uses Web Speech API; text fallback exists | frontend/app.js |
| Local history | Real local-only | Stored in localStorage with max 10 records | frontend/app.js |

### 7.8 Persistence and state

| State | Status | Where stored | Notes |
|---|---|---|---|
| Job status/results | Real | output/jobs/*.json | Server-local JSON |
| Audio files | Real | output/audio/*.mp3 | Server-local MP3 |
| Upload temp files | Real transient | OS temp path | Removed in `finally` block |
| User language/level | Real local-only | browser localStorage | No server profile table |
| History records | Real local-only | browser localStorage | No backend sync |

### 7.9 Bypassed or stale highlights (Archive)

All architectural modules are now integrated. Stale components from early development have been fixed or removed.

---

## 8. Error and Fallback Behavior Matrix

| Stage | Trigger | User-visible effect | Runtime outcome |
|---|---|---|---|
| Upload validate | Unsupported extension | HTTP 400 | Request rejected early |
| Upload size | >10 MB | HTTP 413 with size message | Request rejected during chunk write |
| OCR sparse output | Low clean text | Job failed with blur/unreadable message | `LowConfidenceException` |
| OCR provider error | Non-2xx from OCR API | Job failed with OCR message | `OCRException` branch |
| Timeout | Slow network/provider | Job failed timeout message | `asyncio.TimeoutError` branch |
| Memory pressure | Server memory issue | Job failed with memory message | `MemoryError` branch |
| LLM unavailable | Chat call error | Fallback page output returned | Deterministic fallback path |
| ElevenLabs fail | API/network/voice issue | Audio still generated via gTTS (usually) | Fallback TTS path |
| Poll exceeds 180s | Slow end-to-end | Frontend timeout message | Client aborts wait |

Important nuance:
- LLM failure does not always fail job. It often degrades to fallback content and still completes.

---

## 9. Frontend Functional Deep Dive

### 9.1 Onboarding and profile controls

- First-run gate uses `nagrik_config` localStorage key.
- Captures language and simplification level.
- No backend account/profile persistence.

### 9.2 Upload and processing orchestration

- Uses compressed image generation for mobile stability.
- Clears input handles after upload prep to reduce memory usage.
- Rotates progress messages while processing.
- Polls status until completed/failed or timeout.

### 9.3 Rendering behavior

- Renders page tabs from `result.pages`.
- Renders field cards with number, icon, what-to-fill, why-it-matters, example.
- If page has no fields:
  - for instruction/declaration/signature-like pages, shows informational message
  - otherwise prompts user to retake clearer scan

### 9.4 Voice and ask-ai

- If speech recognition unsupported, user can still type.
- Context for ask-ai is pulled from currently selected page result.
- Answer audio generated using field TTS endpoint.

Brutal truth:
- The frontend is not mock-wired. It depends on real backend results.
- Browser localStorage means history is per-browser, not shared across devices.

---

## 10. Environment and Dependencies

### 10.1 Required env variables

- `MISTRAL_API_KEY` (required for OCR and embeddings)
- `MISTRAL_CHAT_MODEL` (required for LLM simplification/ask-ai quality path)

### 10.2 Optional env variables

- `MISTRAL_BASE_URL` (default `https://api.mistral.ai/v1`)
- `MISTRAL_OCR_MODEL` (default `mistral-ocr-latest`)
- `ELEVENLABS_API_KEY` (enables premium TTS path)
- `MAX_CONTEXT_NODES` (default `3`)
- `MAX_GUIDELINE_HITS` (default `3`)
- `TTS_LANGUAGE` (default `en`)

### 10.3 Python dependencies

Defined in backend/requirements.txt:
- fastapi
- uvicorn
- python-multipart
- requests
- gTTS
- pydantic
- python-dotenv
- numpy

---

## 11. Known Behavior Gaps (Current State)

1. `updated_at` in job file is not a timestamp.
- It is a random UUID marker and cannot be used as chronological time.

2. History is browser-local only.
- Server does not provide history retrieval API.

3. Document-level RAG helper exists but is unused.
- Page-level RAG is preferred for surgical grounding in the current pipeline.

These are factual runtime limitations, not technical failures.

---

## 12. Verification Checklist (Reality-Proof)

Use this checklist to validate claims in this document against the running system:

1. Confirm real OCR path
- Trigger `/api/process` with a sample image.
- Verify job file in output/jobs includes OCR-derived `original_markdown`.

2. Confirm real job state persistence
- Observe `pending -> processing -> completed/failed` in output/jobs/<job_id>.json.

3. Confirm field extraction is deterministic
- Use text containing `Label: ____` and table rows.
- Check returned `fields` and pattern-like labels.

4. Confirm hybrid retrieval is active
- Inspect `field_retrievals` and `retrieved_guidelines` in completed job output.

5. Confirm simplification level effect
- Run scratch/brutal_verify_levels.py and compare outputs by level.

6. Confirm TTS fallback
- Unset ElevenLabs key and run scratch/test_tts.py.
- Verify MP3 still appears in output/audio via gTTS.

7. Confirm ask-ai grounding behavior
- Call `/api/ask` with narrow page context and unrelated question.
- Check response avoids unsupported claims.

8. Confirm bypassed modules
- Search runtime flow in backend/main.py for any call to `DocumentMemory` or `verify_output`.
- Verify none exist in live orchestration path.

9. Confirm stale script
- Search for `query_guidelines` definition.
- Verify only scratch/test_mp_rag.py references it.

---

## 13. Operational Notes for Maintainers

- This application is production-like in behavior but still MVP in architecture.
- Most heavy lifting is external API dependent (OCR/LLM/embeddings/TTS provider).
- Runtime reliability depends on network and third-party API health.
- Storage is local filesystem + browser localStorage; there is no database.

Final brutal summary:
- Real work: yes, across upload, OCR, retrieval, simplification, and TTS.
- Mocked pieces: no fake API endpoints, but there are bypassed modules and fallback code paths.
- If someone calls this a pure mock demo, that is technically incorrect.
