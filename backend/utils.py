from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

TOKEN_RE = re.compile(r"[A-Za-z0-9]+")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
FIELD_RE = re.compile(r"^\s*([A-Za-z\u0900-\u097F][A-Za-z0-9\u0900-\u097F /().,_-]{1,120})\s*[:：\-–—]\s*(.{1,500})\s*$")

def tokenize(text: str) -> list[str]:
    return [t.lower() for t in TOKEN_RE.findall(text or "")]

def score_overlap(query: str, text: str) -> float:
    q_tokens = set(tokenize(query))
    t_tokens = set(tokenize(text))
    if not q_tokens or not t_tokens:
        return 0.0
    overlap = q_tokens & t_tokens
    return len(overlap) / max(1, len(q_tokens))

import numpy as np
import requests
import time
from .config import settings

def get_embedding(text_or_list: str | list[str]) -> list[float] | list[list[list[float]]] | None:
    if not settings.mistral_api_key or not text_or_list:
        return None
    
    is_list = isinstance(text_or_list, list)
    inputs = text_or_list if is_list else [text_or_list]
    # Truncate each input to 8000 chars
    inputs = [t[:8000] for t in inputs]
    
    url = "https://api.mistral.ai/v1/embeddings"
    headers = {
        "Authorization": f"Bearer {settings.mistral_api_key}",
        "Content-Type": "application/json",
    }
    data = {
        "model": "mistral-embed",
        "input": inputs
    }

    max_retries = 3
    backoff = 1.0  # seconds

    for attempt in range(max_retries + 1):
        try:
            resp = requests.post(url, headers=headers, json=data, timeout=30)
            if resp.status_code == 200:
                embeddings = [d["embedding"] for d in resp.json()["data"]]
                return embeddings if is_list else embeddings[0]
            elif resp.status_code == 429:
                if attempt < max_retries:
                    print(f"[Nagrik] Mistral Embedding Rate Limit (429). Retrying in {backoff}s... (Attempt {attempt+1}/{max_retries})")
                    time.sleep(backoff)
                    backoff *= 2
                    continue
                else:
                    print(f"[Nagrik] Mistral Embedding Error: 429 Rate Limit exceeded after {max_retries} retries.")
            else:
                print(f"[Nagrik] Mistral Embedding Error: {resp.status_code} {resp.text}")
                break
        except Exception as e:
            print(f"[Nagrik] Mistral Embedding Exception: {e}")
            break
    return None

def cosine_similarity(vec1: list[float] | None, vec2: list[float] | None) -> float:
    if not vec1 or not vec2:
        return 0.0
    v1 = np.array(vec1)
    v2 = np.array(vec2)
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return float(np.dot(v1, v2) / (norm1 * norm2))


def extract_json_block(text: str) -> dict[str, Any] | None:
    if not text:
        return None
    text = text.strip()
    try:
        return json.loads(text)
    except Exception:
        pass
    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except Exception:
        return None

def first_heading(markdown: str) -> str:
    for line in (markdown or "").splitlines():
        m = HEADING_RE.match(line.strip())
        if m:
            return m.group(2).strip()
    for line in (markdown or "").splitlines():
        clean = line.strip()
        if clean:
            return clean[:120]
    return "Untitled section"

def markdown_to_plain_text(markdown: str) -> str:
    if not markdown:
        return ""
    text = markdown
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"\[(.*?)\]\((.*?)\)", r"\1", text)
    text = re.sub(r"^\s*[-*+]\s+", "- ", text, flags=re.MULTILINE)
    text = re.sub(r"<br\s*/?>", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def safe_read_json(path: str | Path, default: Any) -> Any:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default

def ensure_dir(path: str | Path) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p
