# STRUCTURE.md

## Core Directories

- **`frontend/`**: Vanilla implementation of the single-page application.
  - `index.html`: Shell UI.
  - `app.js`: All client-side polling, DOM manipulation, storage logic, and rendering templates.
  - `style.css`: View styling.

- **`backend/`**: Contains the FastAPI implementation and processing logic.
  - `main.py`: Entrypoint, route definitions, and overall background job orchestration.
  - `config.py`: Environment variable and static configuration loader.
  - `llm.py`: Logic encompassing Mistral chat interactions (page summarization, 'ask AI').
  - `ocr.py`: Mistral OCR integration and initial text/layout processing.
  - `rag.py` & `pageindex_tree.py`: Retrieval Augmented Generation orchestration, creating tree-based document maps.
  - `field_extractor.py` & `validators.py`: Deterministic text processing and warning labeling on extracted fields.
  - `utils.py` & `schema.py`: Internal helpers and Pydantic validation shapes.
  - `memory.py` & `tts.py`: Unwired document memory logic and functional audio generators.

- **`data/`**: Core local databases.
  - `civic_guidelines.json`: Grounding truth used by RAG.

- **`output/`**: Local runtime artifacts.
  - `jobs/`: Job execution files (`.json`).
  - `audio/`: Generated MP3 audio segments.

- **`scratch/`**: Scripts and test environments (e.g., testing MP/RAG algorithms and logic directly).
