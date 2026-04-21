# System Architecture

Nagrik-AI is a full-stack document assistant built with a modular and scalable architecture that bridges modern front-end user experience with advanced backend document intelligence.

The architecture emphasizes **ephemeral processing**, **deep structure retrieval (RAG)**, and **multi-modal outputs (Text & Speech)** to make complex local civic forms understandable for everyday citizens.

---

## 1. High-Level System Design

The system divides responsibilities sharply between the client-side presentation layer and the server-side intelligence pipeline. 

![image](https://www.image2url.com/r2/default/images/1776774822347-2e70154f-de8d-4fb3-811e-b431f1e07b68.png)

### Components:
- **Frontend Layer**: A lightweight Vanilla HTML5/JS/CSS client offering responsive layouts tailored for mobile accessibility.
- **Backend Layer (FastAPI)**: Python-based asynchronous server connecting endpoints to background execution units.
- **Data & Storage Layer**: Contains zero-infrastructure persistent stores (ChromaDB for vectors, local local disk mapping for jobs/audio outputs).

---

## 2. Document Processing Pipeline Workflow

The core functionality of Nagrik-AI is extracting information from a raw image or PDF and mapping it to civic guidelines to return actionable simplification to the citizen.

![image](https://www.image2url.com/r2/default/images/1776774900380-1cc41bf8-3225-47a7-b9f1-9e66a0e158df.png)

---

## 3. Retrieval-Augmented Generation (RAG) & Memory Subsystem

Nagrik-AI doesn't rely purely on LLM parametric memory. It matches user documents against external **Civic Guidelines** via ChromaDB using embeddings.

### Dual-Layer RAG Execution
1. **Document-Level Retrieval**: Uses the core document purpose (e.g. "Passport Application") to fetch broad instructions applying to the entire file.
2. **Field-Level Surgical Retrieval**: Specific form fields (like "*Aadhaar Card*", "*Taluka*") invoke batched queries to ChromaDB. Native batching eliminates `429 Too Many Requests` API errors.

![image](https://www.image2url.com/r2/default/images/1776774951334-b06ebe7f-8e89-4174-a7f0-911ea38d4d8f.png)

### Semantic Memory (Cross-Document Search)
To help citizens remember what they've previously filled out, all processed document chunks are saved in a `document_memory` ChromaDB collection.
- Uses `NagrikEmbeddingFunction` wrapping Mistral embeddings to calculate cosine similarity.
- Enhances retrieval iteratively using keyword boosting + LLM reranking to ensure precise hits among ambiguous forms.

---

## 4. Privacy & Ephemeral Data Flow (Hardening)

Data persistence is strictly governed by a privacy-first Ephemeral Policy. The application clears context dynamically to ensure private civic information doesn't leak across sessions.

![image](https://www.image2url.com/r2/default/images/1776775016287-d1e9de68-4ff5-454c-88af-a392dd94bddc.png)
When `/api/auth/logout` is hit, FastAPI triggers `clear_user_data(user_id)` dropping vectors from Chroma and unlinking transient files from the `output/` tier.
