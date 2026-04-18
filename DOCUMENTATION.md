# Nagrik Civic Translator MVP - Technical Documentation

## 1. Executive Summary
Nagrik is a voice-first civic document assistant designed for rural accessibility in India. It transforms complex government documents (PDFs/Images) into simplified, localized instructions with high-fidelity voice output. 

---

## 2. Technical Audit: Reality Check
This document describes the *actual* behavior of the system as integrated today.

### 2.1 Reality Matrix

| Area | Status | Reality | Evidence |
| :--- | :--- | :--- | :--- |
| **OCR Utility** | **Hardened** | Multi-page text/layout extraction | `backend/ocr.py` |
| **Field Extractor** | **Robust** | Regex-based heuristic form detection | `backend/field_extractor.py` |
| **Document Graph** | **Integrated** | Structural memory & section linkage | `backend/document_graph.py` |
| **Session Memory** | **Integrated** | Cross-turn conversation state | `backend/session_memory.py` |
| **Hybrid RAG** | **Optimized** | Guideline retrieval (Semantic + Keyword) | `backend/rag.py` |
| **LLM Grounding** | **Integrated** | Simplification & hallucination checks | `backend/llm.py` |
| **TTS System** | **Hardened** | Multi-provider (ElevenLabs/gTTS) audio | `backend/tts.py` |

---

## 3. Repository Map

- **Backend**
  - `backend/main.py`: API routes & job orchestration
  - `backend/ocr.py`: Mistral OCR integration
  - `backend/document_graph.py`: Structural section graph
  - `backend/session_memory.py`: Conversation state manager
  - `backend/rag.py`: Guideline retrieval logic
  - `backend/llm.py`: Grounded simplification & QA
  - `backend/field_extractor.py`: Form field heuristics
  - `backend/tts.py`: Audio generation

- **Frontend**
  - `frontend/app.js`: Main SPA logic (polling, upload, chat)
  - `frontend/index.html`: Mobile-first UI

---

## 4. End-to-End Runtime Pipeline

1. **Intake**: Frontend compresses images and POSTs to `/api/process`.
2. **OCR**: Mistral Files/OCR extracts markdown and bounding blocks.
3. **Structure**: `DocumentGraph` parses headers and links sections across pages.
4. **Retrieval**: Guidelines retrieved per page and per field with semantic scoring.
5. **Simplification**: LLM generates localized, grounded summaries.
6. **TTS**: Summary audio generated (premium or standard fallback).
7. **Polling**: User UI adaptively polls until results are ready.

---

## 5. API Reference

### 5.1 POST `/api/process`
- **Fields**: `file`, `language`, `level`, `lightweight`.
- **Logic**: Enforces 10MB limit and starts async background job.

### 5.2 POST `/api/ask`
- **Fields**: `question`, `job_id`, `session_id`.
- **Logic**: Traverses Graph + Session Memory to resolve multi-page references.

---

## 6. Competitive Landscape

| Feature | Nagrik AI | ChatGPT / Claude | Generic PDF Bots |
| :--- | :--- | :--- | :--- |
| **Domain focus** | **Indian Civic Forms** | General Purpose | Business PDFs |
| **Language** | **Hindi-First** | Generic Translation | Poor non-English |
| **Context Logic** | **DocumentGraph (Structural)** | Single Window (Flat) | Keyword/Vector (Flat) |
| **Accessibility** | **Voice-First / Mobile** | Text-heavy / Desktop | Web/Desktop only |
| **Grounding** | **Validated Guidelines** | Hallucination risk | Uncontrolled RAG |

---

## 7. Visual System Architecture

### 7.1 End-to-End User Flow
![image](https://www.image2url.com/r2/default/images/1776475211550-b06f1a82-5174-4c44-a850-b2d6257394ca.png)

### 7.2 Async Processing Pipeline (The "Job" Flow)
![image](https://www.image2url.com/r2/default/images/1776475265016-5c9c2d29-f10a-435f-8aad-7fb9d874d1f6.png)

### 7.3 AI Chatbot & Memory Logic
![image](https://www.image2url.com/r2/default/images/1776475303450-31e9dd49-fcb7-4dc3-98cb-6cc3224e1727.png)

### 7.4 TTS Fallback Strategy
![image](https://www.image2url.com/r2/default/images/1776475381773-26b5a0be-8828-4693-a546-8b1c8e6dc356.png)

