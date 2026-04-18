from __future__ import annotations

from pathlib import Path
from typing import Any
import requests
import re
import logging
import time

from .config import settings

logger = logging.getLogger(__name__)

class OCRException(RuntimeError):
    pass

class LowConfidenceException(OCRException):
    pass

def _headers() -> dict[str, str]:
    if not settings.mistral_api_key:
        raise OCRException("MISTRAL_API_KEY is missing.")
    return {
        "Authorization": f"Bearer {settings.mistral_api_key}",
    }

def upload_file_to_mistral(file_path: str, purpose: str = "ocr") -> str:
    url = f"{settings.mistral_base_url}/files"
    max_retries = 2
    for attempt in range(max_retries + 1):
        try:
            with open(file_path, "rb") as f:
                files = {"file": (Path(file_path).name, f)}
                data = {"purpose": purpose, "visibility": "user"}
                resp = requests.post(url, headers=_headers(), files=files, data=data, timeout=120)
            
            if resp.status_code == 200:
                payload = resp.json()
                break
            elif resp.status_code in [429, 503, 504]:
                if attempt < max_retries:
                    time.sleep(2 ** attempt)
                    continue
            raise OCRException(f"File upload failed: {resp.status_code} {resp.text}")
        except Exception as e:
            if attempt < max_retries:
                time.sleep(1)
                continue
            raise e
    file_id = payload.get("id")
    if not file_id:
        raise OCRException("Upload succeeded but no file_id was returned.")
    return file_id

def _parse_markdown_blocks(markdown: str) -> list[dict[str, Any]]:
    # Very basic block parser saving structure instead of flattening to text
    blocks = []
    paragraphs = markdown.split("\n\n")
    for p in paragraphs:
        p = p.strip()
        if not p:
            continue
        block_type = "paragraph"
        if p.startswith("#"):
            block_type = "heading"
        elif p.startswith("|") and "-|-" in p:
            block_type = "table"
        elif p.startswith("- ") or p.startswith("* ") or re.match(r"^\d+\.", p):
            block_type = "list"
        
        # Calculate block confidence
        confidence = 0.9
        clean_len = len(re.sub(r'[^a-zA-Z0-9\u0900-\u097F]', '', p))
        if clean_len < 5 and len(p) > 10:
            confidence = 0.3
        elif p.count('?') > 3 or p.count('▪') > 3:
            confidence = 0.4
        
        blocks.append({
            "type": block_type,
            "content": p,
            "confidence": confidence
        })
    return blocks

def run_ocr(file_path: str, filename: str | None = None, pages: list[int] | None = None) -> dict[str, Any]:
    file_id = upload_file_to_mistral(file_path, purpose="ocr")
    url = f"{settings.mistral_base_url}/ocr"
    body = {
        "model": settings.mistral_ocr_model,
        "document": {"file_id": file_id},
    }
    if pages is not None:
        body["pages"] = pages

    max_retries = 2
    for attempt in range(max_retries + 1):
        try:
            resp = requests.post(url, headers={**_headers(), "Content-Type": "application/json"}, json=body, timeout=300)
            if resp.status_code == 200:
                data = resp.json()
                break
            elif resp.status_code in [429, 503, 504]:
                if attempt < max_retries:
                    time.sleep(5) # Wait longer for OCR
                    continue
            raise OCRException(f"OCR failed: {resp.status_code} {resp.text}")
        except Exception as e:
            if attempt < max_retries:
                time.sleep(2)
                continue
            raise e
    extracted_pages = []
    
    for p in data.get("pages", []):
        index = p.get("index")
        markdown = p.get("markdown") or ""
        
        # Confidence Check: If markdown is exceptionally short and isn't just an image, it's likely a bad scan
        # Include Devanagari (Hindi/Marathi), Bengali, Tamil, Telugu, Kannada, Malayalam, Gujarati, Odia
        clean_text = re.sub(r'[^a-zA-Z0-9\u0900-\u097F\u0980-\u09FF\u0A00-\u0A7F\u0B00-\u0B7F\u0B80-\u0BFF\u0C00-\u0C7F\u0C80-\u0CFF\u0D00-\u0D7F]', '', markdown)
        logger.info(f"[Nagrik] Page {index} extracted text length: {len(clean_text)}")
        
        # Lowered threshold from 20 to 5 to handle sparse forms/stamps
        if len(clean_text) < 5 and not p.get("images"):
            logger.warning(f"Low confidence on page {index}. Text too sparse ({len(clean_text)} chars).")
            raise LowConfidenceException("The image is too blurry or unreadable. Please retake the photo in better lighting.")
        
        blocks = _parse_markdown_blocks(markdown)
        
        extracted_pages.append({
            "page": int(index) if index is not None else len(extracted_pages) + 1,
            "markdown": markdown,
            "blocks": blocks, # Saving layout signals!
            "images": p.get("images", []),
            "dimensions": p.get("dimensions", {}),
        })

    if not extracted_pages:
        raise LowConfidenceException("No pages could be extracted. Please ensure the document is clear.")

    return {
        "file_id": file_id,
        "model": data.get("model", settings.mistral_ocr_model),
        "pages": extracted_pages,
    }
