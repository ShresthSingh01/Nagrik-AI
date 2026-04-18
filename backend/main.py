import asyncio
import json
import os
import tempfile
import uuid
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, Form, HTTPException, UploadFile, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .config import settings
from .field_extractor import extract_fields_from_markdown
from .llm import simplify_page, ask_ai
from .ocr import OCRException, run_ocr, LowConfidenceException
from .pageindex_tree import build_pageindex_tree
from .rag import load_guidelines, retrieve_context, retrieve_document_context, retrieve_field_context_batch
from .schema import SimplificationLevel
from .tts import text_to_speech

from .session_memory import SessionMemory
from .document_graph import DocumentGraph, GraphNode
from .memory import DocumentMemory
from .utils import ensure_dir, safe_read_json
from .validators import validate_fields

_GRAPHS: dict[str, DocumentGraph] = {}

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
OUTPUT_DIR = ensure_dir(BASE_DIR / "output")
AUDIO_DIR = ensure_dir(OUTPUT_DIR / "audio")
JOBS_DIR = ensure_dir(OUTPUT_DIR / "jobs")
UPLOAD_CHUNK_SIZE = 1024 * 1024
MAX_UPLOAD_BYTES = 10 * 1024 * 1024

app = FastAPI(title="Nagrik Document Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")
app.mount("/audio", StaticFiles(directory=str(AUDIO_DIR)), name="audio")

@app.on_event("startup")
def startup_event():
    if settings.mistral_api_key:
        print("[Nagrik] Pre-embedding Civic Guidelines...")
        load_guidelines()

@app.get("/")
def root():
    return FileResponse(str(FRONTEND_DIR / "index.html"))

@app.get("/api/health")
def health():
    return {
        "ok": True,
        "mistral_configured": bool(settings.mistral_api_key),
    }

# --- Job Status Helpers ---

def _update_job_status(job_id: str, status: str, data: Any = None, error: str = None):
    job_path = JOBS_DIR / f"{job_id}.json"
    job_data = {
        "id": job_id,
        "status": status,
        "updated_at": uuid.uuid4().hex, # Dummy update marker
    }
    if data:
        job_data["result"] = data
    if error:
        job_data["error"] = error
    
    with open(job_path, "w", encoding="utf-8") as f:
        json.dump(job_data, f)

async def _save_upload_to_tempfile(upload: UploadFile, suffix: str) -> tuple[str, int]:
    fd, tmp_path = tempfile.mkstemp(suffix=suffix)
    total_bytes = 0
    try:
        with os.fdopen(fd, "wb") as tmp:
            while True:
                chunk = await upload.read(UPLOAD_CHUNK_SIZE)
                if not chunk:
                    break
                total_bytes += len(chunk)
                if total_bytes > MAX_UPLOAD_BYTES:
                    raise HTTPException(
                        status_code=413,
                        detail="File is too large. Maximum allowed size is 10 MB.",
                    )
                tmp.write(chunk)
    except Exception:
        Path(tmp_path).unlink(missing_ok=True)
        raise
    finally:
        await upload.close()

    return tmp_path, total_bytes

async def _process_page_async(
    page: dict[str, Any],
    language: str,
    tree: Any,
    guidelines: Any,
    document_context: dict[str, Any],
    level: SimplificationLevel,
    lightweight: bool = False,
    user_profile: str = "",
):
    page_num = int(page["page"])
    page_md = page.get("markdown") or ""
    blocks = page.get("blocks", [])

    print(f"[Nagrik] Analysis started for Page {page_num}")

    # Layout analysis
    detected_fields = await asyncio.to_thread(extract_fields_from_markdown, page_md)
    print(f"[Nagrik] Page {page_num}: Regex extractor found {len(detected_fields)} fields"  + (f" ({', '.join(f['label'] for f in detected_fields[:5])})" if detected_fields else ""))

    # RAG retrieval
    query = page_md[:1200]
    context = await asyncio.to_thread(
        retrieve_context, query, tree, guidelines, page_num, lightweight
    )

    # Blend global document guidance with local page guidance.
    context["document_guideline_hits"] = document_context.get("guideline_hits", [])

    # NEW: Field-level RAG for Surgical Grounding (Hardening 1 - BATCH OPTIMIZED)
    field_retrievals = {}
    if not lightweight and detected_fields:
        print(f"[Nagrik] Performing field-level retrieval for {len(detected_fields)} fields in ONE batch...")
        
        # Collect labels that need context
        labels_to_fetch = [f.get("label") for f in detected_fields if f.get("label") and len(f.get("label")) >= 3]
        
        # ONE single API call for all labels combined (Eliminates 429 errors)
        batch_hits = await asyncio.to_thread(retrieve_field_context_batch, labels_to_fetch, guidelines)
        
        for label, hit in batch_hits.items():
            field_retrievals[label] = {
                "title": hit["guideline"].get("title"),
                "description": hit["guideline"].get("description"),
                "score": hit["score"]
            }

    # All-in-one simplification (Classify + Simplify)
    page_output = await asyncio.to_thread(
        simplify_page,
        language=language,
        page_num=page_num,
        page_markdown=page_md,
        context=context,
        detected_fields=detected_fields,
        field_retrievals=field_retrievals, # Passed for grounding
        level=level,
        user_profile=user_profile,
    )


    # Confidence Mapping
    unclear_blocks = [b for b in blocks if b.get("confidence", 1.0) < 0.5]
    if unclear_blocks:
        page_output.setdefault("warnings", []).append(
            "[UNCLEAR] A section of this page was hard to read. Double-check your actual form."
        )

    # Rule-based validation
    field_warnings = validate_fields(page_output.get("fields", []))
    if field_warnings:
        page_output.setdefault("warnings", []).extend(field_warnings)

    print(f"[Nagrik] Analysis complete for Page {page_num}")
    return page_output

async def _run_analysis_job(
    job_id: str,
    tmp_path: str,
    filename: str,
    language: str,
    simplification_level: SimplificationLevel,
    lightweight: bool,
    user_profile: str
):
    try:
        _update_job_status(job_id, "processing")
        
        print(f"[Nagrik] Running OCR for: {filename}")
        ocr_result = await asyncio.to_thread(run_ocr, tmp_path, filename=filename, pages=[0, 1, 2])
        pages = ocr_result["pages"]

        # Redundant slicing removed as OCR is now targeted

        print(f"[Nagrik] Building DocumentGraph (Cross-Page Memory Ready)...")
        graph = DocumentGraph()
        graph.build(pages)
        _GRAPHS[job_id] = graph
        
        # Legacy tree for backward compatibility if needed, but graph is primary
        tree = build_pageindex_tree(pages)
        guidelines = load_guidelines()

        print("[Nagrik] Retrieving document-level guidance...")
        document_context = await asyncio.to_thread(
            retrieve_document_context,
            tree,
            guidelines,
            lightweight,
        )

        # Parallelize Page Processing
        print(f"[Nagrik] Starting parallel analysis for {len(pages)} pages...")
        tasks = [
            _process_page_async(
                page,
                language,
                tree,
                guidelines,
                document_context,
                simplification_level,
                lightweight,
                user_profile,
            )
            for page in pages
        ]
        page_results = list(await asyncio.gather(*tasks))
        
        # NEW: Integrate DocumentMemory (Fixing bypassed check from DOCUMENTATION.md)
        # Scan all pages for repeatable facts (Name, Aadhaar, etc.) and inject cross-page hints
        print(f"[Nagrik] Running cross-page memory enrichment...")
        page_results = DocumentMemory().enrich_pages(page_results)

        # Build Action-Oriented TTS Script
        audio_script_parts = []
        purpose_seen = set()
        for item in page_results:
            purpose = item.get("document_purpose", "")
            action = item.get("action_guide", "")
            warnings = item.get("warnings", [])

            if purpose and purpose not in purpose_seen:
                audio_script_parts.append(f"Document Purpose: {purpose}.")
                purpose_seen.add(purpose)
            
            real_warnings = [w for w in warnings if "Fallback mode" not in w]
            if real_warnings:
                audio_script_parts.append("Important: " + ". ".join(real_warnings[:2]) + ".")
            if action:
                audio_script_parts.append(f"On Page {item.get('page')}, {action}.")

        tts_script = " ".join(audio_script_parts).strip()
        if not tts_script:
            tts_script = "The document was processed successfully. Please review the text instructions."

        audio_name = f"{uuid.uuid4().hex}.mp3"
        audio_path = str(AUDIO_DIR / audio_name)
        audio_url = None
        if not lightweight:
            print(f"[Nagrik] Generating summary audio ({language})...")
            tts_lang = "hi" if language == "Hindi" else "en"
            await asyncio.to_thread(text_to_speech, tts_script, audio_path, lang=tts_lang)
            audio_url = f"/audio/{audio_name}"

        # Create dynamic summary
        first_page_purpose = page_results[0].get("document_purpose", "Document") if page_results else "Document"
        if language == "English":
            dynamic_summary = f"{first_page_purpose}. Fill in the details in the sections below. If any part is unclear, listen to the audio guide."
            low_data_label = " (Low Data Mode)"
        else:
            dynamic_summary = f"{first_page_purpose}. यह फॉर्म सरकारी मदद के लिए है। नीचे बताई गई जगहों में सही जानकारी भरें। अगर कोई हिस्सा समझ न आए, आवाज़ में सुनें।"
            low_data_label = " (कम डेटा मोड)"
        
        result_data = {
            "filename": filename,
            "language": language,
            "level": simplification_level.value,
            "overall_summary": dynamic_summary + (low_data_label if lightweight else ""),
            "pages": page_results,
            "audio_url": audio_url,
        }
        
        _update_job_status(job_id, "completed", data=result_data)
        print(f"[Nagrik] Analysis Completed: {job_id}")

    except LowConfidenceException as e:
        print(f"[Nagrik] Job Low Confidence: {e}")
        _update_job_status(job_id, "failed", error=str(e))
    except OCRException as e:
        error_msg = str(e)
        print(f"[Nagrik] Job OCR Error: {error_msg}")
        # Keep user-friendly error but append technical hint if appropriate
        friendly_error = "Could not read the document clearly. Please retake the photo in better lighting."
        if "401" in error_msg or "403" in error_msg:
            friendly_error = "Technical Error: API Key Authorization failed. Please check your Mistral settings."
        elif "429" in error_msg:
            friendly_error = "Server is busy. Please wait a few moments and try again."
        
        _update_job_status(job_id, "failed", error=friendly_error)
    except asyncio.TimeoutError:
        print("[Nagrik] Job Timeout Error")
        _update_job_status(
            job_id,
            "failed",
            error="Processing timed out on a slow network. Please retry with a smaller or clearer image.",
        )
    except MemoryError:
        print("[Nagrik] Job Memory Error")
        _update_job_status(
            job_id,
            "failed",
            error="Processing ran out of memory. Please upload a smaller file (up to 10 MB).",
        )
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"[Nagrik] Job Error: {error_detail}")
        _update_job_status(
            job_id,
            "failed",
            error=f"Processing failed unexpectedly ({type(e).__name__}). Please retry once or upload a smaller image.",
        )
    finally:
        Path(tmp_path).unlink(missing_ok=True)

@app.post("/api/process")
async def process(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    language: str = Form("English"),
    level: int = Form(2),
    lightweight: bool = Form(False),
    user_profile: str = Form(""),
):
    allowed_ext = {".pdf", ".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff"}
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in allowed_ext:
        raise HTTPException(status_code=400, detail="Only PDF and image files are supported.")

    try:
        simplification_level = SimplificationLevel(level)
    except ValueError:
        simplification_level = SimplificationLevel.SIMPLE

    # Save to temp file in chunks to avoid loading the full upload in memory.
    tmp_path, _ = await _save_upload_to_tempfile(file, suffix)

    job_id = f"job_{uuid.uuid4().hex[:12]}"
    _update_job_status(job_id, "pending")
    
    # Start background execution
    background_tasks.add_task(
        _run_analysis_job, 
        job_id, 
        tmp_path, 
        file.filename, 
        language, 
        simplification_level, 
        lightweight, 
        user_profile
    )
    
    return JSONResponse({"job_id": job_id})

@app.get("/api/status/{job_id}")
async def get_status(job_id: str):
    job_path = JOBS_DIR / f"{job_id}.json"
    if not job_path.exists():
        raise HTTPException(status_code=404, detail="Job not found")
    
    data = safe_read_json(job_path, default={})
    return JSONResponse(data)

@app.post("/api/ask")
async def process_ask_ai(
    question: str = Form(...),
    page_context: str = Form(""),
    page_summary: str = Form(""),
    guideline_context: str = Form(""),
    field_context: str = Form(""),
    language: str = Form("English"),
    session_id: str = Form("default"),
    job_id: str = Form(""),
):
    from .rag import retrieve_expanded_context
    
    expanded_context = []
    if job_id and job_id in _GRAPHS:
        graph = _GRAPHS[job_id]
        guidelines = load_guidelines()
        rag_res = await asyncio.to_thread(retrieve_expanded_context, question, graph, guidelines)
        expanded_context = rag_res.get("tree_hits", [])

    answer_data = await asyncio.to_thread(
        ask_ai, 
        question, 
        page_context, 
        page_summary, 
        guideline_context, 
        field_context, 
        language,
        session_id=session_id,
        expanded_context=expanded_context
    )
    
    # Update Session Memory
    SessionMemory.update_session(
        session_id, 
        last_query=question, 
        last_answer=answer_data.get("answer"),
        cited_pages=answer_data.get("pages_cited", [])
    )
    
    return JSONResponse(answer_data)

@app.post("/api/tts-field")
async def generate_field_tts(
    text: str = Form(...),
    lang: str = Form("en"),
):
    audio_name = f"field_{uuid.uuid4().hex[:8]}.mp3"
    audio_path = str(AUDIO_DIR / audio_name)
    await asyncio.to_thread(text_to_speech, text, audio_path, lang=lang)
    return JSONResponse({"audio_url": f"/audio/{audio_name}"})
