from __future__ import annotations

import json
import logging
import hashlib
from pathlib import Path
from typing import Any

import chromadb
from chromadb.api.types import EmbeddingFunction, Documents, Embeddings

from .config import settings
from .pageindex_tree import best_tree_nodes
from .document_graph import DocumentGraph
from .utils import safe_read_json, score_overlap, get_embedding, ensure_dir

logger = logging.getLogger(__name__)

# --- Paths ---
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "civic_guidelines.json"
CHROMA_PATH = BASE_DIR / "output" / "chroma_db"

# --- Globals ---
_CHROMA_CLIENT: chromadb.PersistentClient | None = None
_COLLECTION: chromadb.Collection | None = None

# --- Custom Embedding Function for ChromaDB ---
class NagrikEmbeddingFunction(EmbeddingFunction):
    def __call__(self, input: Documents) -> Embeddings:
        """Wraps Mistral embeddings for ChromaDB."""
        # ChromaDB 'Documents' is basically a list[str]
        res = get_embedding(list(input))
        if res is None:
            logger.error("[Nagrik] Mistral embedding failed during ChromaDB operation.")
            # Fallback to zero vectors to prevent hard crash, though not ideal
            return [[0.0] * 1024 for _ in input]
        return res

def _get_collection() -> chromadb.Collection:
    global _CHROMA_CLIENT, _COLLECTION
    if _COLLECTION is not None:
        return _COLLECTION
    
    ensure_dir(CHROMA_PATH)
    # Initialize Persistent Client (Zero-Infrastructure)
    _CHROMA_CLIENT = chromadb.PersistentClient(path=str(CHROMA_PATH))
    
    # Mistral embed size is 1024. HNSW cosine space for best semantic match.
    _COLLECTION = _CHROMA_CLIENT.get_or_create_collection(
        name="civic_guidelines",
        embedding_function=NagrikEmbeddingFunction(),
        metadata={"hnsw:space": "cosine"}
    )
    return _COLLECTION

def load_guidelines() -> list[dict[str, Any]]:
    """
    Initializes ChromaDB and populates it from JSON if empty or changed.
    Returns the raw list for legacy compatibility.
    """
    collection = _get_collection()
    
    data = safe_read_json(DATA_PATH, default=[])
    guidelines = data if isinstance(data, list) else []
    
    # Simple sync logic: if count differs, re-index
    count = collection.count()
    if count != len(guidelines) and len(guidelines) > 0:
        print(f"[Nagrik] Syncing ChromaDB collection ({count} -> {len(guidelines)} entries)...")
        
        ids = []
        documents = []
        metadatas = []
        
        for i, item in enumerate(guidelines):
            # Create stable deterministic ID
            uid = "gl_" + hashlib.md5(str(item.get("title", i)).encode()).hexdigest()[:12]
            
            # Text blob for embedding (Title + Keywords + Description)
            text_blob = " ".join([
                str(item.get("title", "")),
                " ".join(item.get("keywords", []) if isinstance(item.get("keywords"), list) else []),
                str(item.get("description", ""))
            ])
            
            ids.append(uid)
            documents.append(text_blob)
            
            metadatas.append({
                "title": str(item.get("title", "")),
                "description": str(item.get("description", "")),
                "keywords": ",".join(item.get("keywords", []) if isinstance(item.get("keywords"), list) else ""),
                "index": i
            })
        
        # Batch upsert
        collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )
        print(f"[Nagrik] ChromaDB populated with {len(guidelines)} guidelines.")
    
    return guidelines

def retrieve_field_context_batch(field_labels: list[str], guidelines: Any = None) -> dict[str, dict[str, Any]]:
    """
    Optimized batch query using ChromaDB's native batch capability.
    Reduces N API calls to 1.
    """
    if not field_labels:
        return {}
    
    collection = _get_collection()
    unique_labels = list(set(field_labels))
    
    # Native batch query across all unique labels
    res = collection.query(
        query_texts=unique_labels,
        n_results=1
    )
    
    results = {}
    for i, label in enumerate(unique_labels):
        if res["ids"] and res["ids"][i]:
            distance = res["distances"][i][0] if res["distances"] else 1.0
            meta = res["metadatas"][i][0] if res["metadatas"] else {}
            
            # Distance 0.0 = Perfect match, 1.0 = No match
            score = max(0.0, 1.0 - distance)
            if score > 0.2: # Threshold for field-level accuracy
                results[label] = {
                    "score": round(score, 3),
                    "guideline": {
                        "title": meta.get("title"),
                        "description": meta.get("description")
                    }
                }
                
    return results

def retrieve_context(query: str, tree: dict[str, Any], guidelines: Any, page_num: int | None = None, skip_embedding: bool = False) -> dict[str, Any]:
    """Retrieve both structural and civic guideline context."""
    tree_hits = best_tree_nodes(query, tree, page_num=page_num, limit=settings.max_context_nodes)
    
    collection = _get_collection()
    
    # Query ChromaDB for top-N guideline hits
    res = collection.query(
        query_texts=[query],
        n_results=settings.max_guideline_hits
    )
    
    guideline_hits = []
    if res["ids"] and res["ids"][0]:
        for i in range(len(res["ids"][0])):
            distance = res["distances"][0][i]
            meta = res["metadatas"][0][i]
            
            score = max(0.0, 1.0 - distance)
            if score > 0.1: # Threshold for page-level relevance
                guideline_hits.append({
                    "score": round(score, 3),
                    "guideline": {
                        "title": meta.get("title"),
                        "description": meta.get("description")
                    }
                })
    
    return {
        "tree_hits": tree_hits,
        "guideline_hits": guideline_hits,
    }

def retrieve_expanded_context(
    query: str, 
    graph: DocumentGraph, 
    guidelines: Any, 
    page_num: int | None = None
) -> dict[str, Any]:
    """
    Advanced retrieval: find nodes and expand them using structural adjacency.
    """
    # 1. Structural search with expansion
    expanded_tree_hits = graph.search(query, limit=settings.max_context_nodes)
    
    # 2. Page-level guideline retrieval (Base RAG)
    collection = _get_collection()
    res = collection.query(
        query_texts=[query],
        n_results=settings.max_guideline_hits
    )
    
    guideline_hits = []
    if res["ids"] and res["ids"][0]:
        for i in range(len(res["ids"][0])):
            distance = res["distances"][0][i]
            meta = res["metadatas"][0][i]
            score = max(0.0, 1.0 - distance)
            if score > 0.1:
                guideline_hits.append({
                    "score": round(score, 3),
                    "guideline": {
                        "title": meta.get("title"),
                        "description": meta.get("description")
                    }
                })
    
    return {
        "tree_hits": expanded_tree_hits,
        "guideline_hits": guideline_hits,
    }

def retrieve_document_context(tree: dict[str, Any], guidelines: Any, skip_embedding: bool = False) -> dict[str, Any]:
    """Retrieves document-level guidelines (for 전체 summary grounding)."""
    root_title = tree.get("title", "")
    collection = _get_collection()
    
    res = collection.query(
        query_texts=[root_title],
        n_results=2
    )
    
    guideline_hits = []
    if res["ids"] and res["ids"][0]:
        for i in range(len(res["ids"][0])):
            distance = res["distances"][0][i]
            meta = res["metadatas"][0][i]
            score = max(0.0, 1.0 - distance)
            if score > 0.1:
                guideline_hits.append({
                    "score": round(score, 3),
                    "guideline": {
                        "title": meta.get("title"),
                        "description": meta.get("description")
                    }
                })
                
    return {
        "guideline_hits": guideline_hits
    }
