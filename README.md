<div align="center">
  <img src="frontend/assets/logo.png" alt="Nagrik-AI Logo" width="200" style="border-radius: 15px; margin-bottom: 20px;" />
  <h1>🏛️ Nagrik-AI Document Assistant</h1>
  <p><strong>Empowering Citizens through Intelligent, Accessible Document Guidance</strong></p>

  <p>
    <a href="https://nagrik-ai-production.up.railway.app/" target="_blank">
      <img src="https://img.shields.io/badge/🚀_Live_Demo-Try_Nagrik--AI_Now!-0052FF?style=for-the-badge&logo=rocket&logoColor=white&boxShadow=0px_4px_10px_rgba(0,0,0,0.1)" alt="Live Demo Link" />
    </a>
  </p>

  <p>
    <a href="#-key-features">Key Features</a> •
    <a href="#-system-architecture">Architecture</a> •
    <a href="#%EF%B8%8F-tech-stack">Tech Stack</a> •
    <a href="#-quick-start">Quick Start</a>
  </p>
</div>

---

Nagrik-AI is a full-stack, local-first document assistant designed to demystify complex civic documents. By harnessing the power of **Mistral OCR** and **Local Civic Knowledge Bases**, Nagrik-AI bridges the accessibility gap, converting dense bureaucratic forms into actionable, plain-language audio and text guides for citizens.

## 🚀 Key Features

- **High-Fidelity Contextual Extraction**: Utilizes Mistral OCR to pull structural knowledge and layout features from both modern PDFs and blurry legacy government documents.
- **Hierarchical Page Indexing (PageIndex)**: Automatically parses extracted documents into a smart semantic tree structure, identifying sections, subsections, and critical form fields to ensure precise, page-aware context mapping during RAG queries.
- **Dual-Layer RAG Engine**: Infuses global document instructions alongside localized semantic form-field guidance (e.g. Aadhaar references, specific taluka guidance) using ChromaDB vector lookups.
- **Multilingual Voice Assistance (TTS)**:  Elevenlabs Instant Text-to-Speech synthesis translates parsed technical civic language into accessible spoken Hindi or English summaries directly into the user interface.Fallback method uses gTTS.
- **Ephemeral Session Memory**: A strict privacy-first pipeline ensures all memory vectors and cached document graphs are thoroughly cleared upon user logout.

## 🧠 System Architecture

The project maintains a sharp detachment between its rapid interactive frontend and its asynchronous Python AI pipelines. 

> [!NOTE]
> For an in-depth view of the system design regarding Vector Embeddings, Background Workflows, and Data Persistence, please refer to the **[Architecture Documentation Here](file:Nagrik-AI/ARCHITECTURE.md)**.

### High-Level Flow
1. **User Input** flows from the frontend interface to a FastAPI asynchronous endpoint.
2. Background tasks trigger **OCR Parsing**. 
3. Parsed fragments invoke **ChromaDB Queries** to apply civic knowledge via **RAG (Retrieval-Augmented Generation)**.
4. Clean results are sent through the **LLM Pipeline**, converting them into simplified language context.
5. Voice summaries are synthesized via the **TTS module**.

## 🛠️ Tech Stack

### Client Layer
* **HTML5 / CSS3 / JavaScript (Vanilla)**: High-performance, lightweight asset delivery with modern glassmorphic implementations.

### Service Layer 
* **[FastAPI](https://fastapi.tiangolo.com/)**: Asynchronous Python micro-framework routing job states across threadpools.
* **[Uvicorn](https://www.uvicorn.org/)**: Blazing-fast ASGI web server implementation.

### AI & Intelligence
* **Mistral AI**: State-of-the-art inference engine managing OCR extraction and prompt parsing.
* **[ChromaDB](https://www.trychroma.com/)**: Embedded vector search handling persistent and ephemeral user semantic mapping.
* **[ElevenLabs](https://elevenlabs.io/)**: Instant Text-to-Speech synthesis for high-quality voice generation.
* **[gTTS](https://gtts.readthedocs.io/en/latest/)**: Google Text-to-Speech library localized for Indic language context outputs.

---

## ⚡ Quick Start

### Prerequisites
- Python `3.10+` minimum.
- A functional Mistral AI API key (add to `.env` or run the setup routine).

### 1️⃣ Launch via Bootstrapper (Recommended for Windows)

The easiest way to initialize the application is through the bundled PowerShell bootstrapper. It sets up your virtual environment, grabs dependencies, securely handles templates, and boots hot-reloading:

```powershell
./scripts/start_server.ps1
```

### 2️⃣ Manual Setup

If you prefer building the environment natively without bootstrapping:

```bash
# 1. Create and source a Virtual Environment
python -m venv .venv
source .venv/bin/activate  # via PS: .\.venv\Scripts\Activate.ps1

# 2. Bind application requirements
pip install -r backend/requirements.txt

# 3. Environment Config Injection
cp .env.example .env
# Open `.env` and assign your Mistral configuration.

# 4. Initiate Server
python -m uvicorn backend.main:app --reload
```
View the graphical interface instantly on `http://127.0.0.1:8000`.

## 📂 Project Structure

```text
Nagrik-AI/
├── backend/          # Edge-facing logic, RAG ingestion pipelines, Vector logic
├── frontend/         # Responsive glassmorphic GUI & State Management Hooks
├── data/             # Static Civic Rulesets and Auth Schemas
├── output/           # (Volatile) Ephemeral Storage for Job Context / Generated Audio
├── scripts/          # Server Bootstrap & Environment Utility Scripts
└── ARCHITECTURE.md   # Advanced systemic sequence mappings and dataflow outlines
```

## 🔒 Security Posture

Nagrik-AI champions right-to-privacy rulesets. 
No persistent identity tracking takes flight beyond isolated JSON memory allocations. Session bounds explicitly clear **ChromaDB Vector embeddings**, **Audio mp3 footprints**, and **Task Context JSONs** whenever the `/api/auth/logout` endpoint is invoked. 

Keep your `.env` securely vaulted and excluded from upstream version control via `.gitignore`. 

---
<div align="center">
  <i>Developed for community enhancement and civic inclusion.
  made with ❤️ by AlgoHolics</i>
</div>
