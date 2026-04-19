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
from .llm import simplify_page, ask_ai, rerank_memory_results

logger = logging.getLogger(__name__)

# --- Paths ---
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "civic_guidelines.json"
CHROMA_PATH = BASE_DIR / "output" / "chroma_db"

# --- Globals ---
_CHROMA_CLIENT: chromadb.PersistentClient | None = None
_COLLECTION: chromadb.Collection | None = None
_MEM_COLLECTION: chromadb.Collection | None = None

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
    if _CHROMA_CLIENT is None:
        _CHROMA_CLIENT = chromadb.PersistentClient(path=str(CHROMA_PATH))
    
    # Mistral embed size is 1024. HNSW cosine space for best semantic match.
    _COLLECTION = _CHROMA_CLIENT.get_or_create_collection(
        name="civic_guidelines",
        embedding_function=NagrikEmbeddingFunction(),
        metadata={"hnsw:space": "cosine"}
    )
    return _COLLECTION

def _get_memory_collection() -> chromadb.Collection:
    global _CHROMA_CLIENT, _MEM_COLLECTION
    if _MEM_COLLECTION is not None:
        return _MEM_COLLECTION
    
    ensure_dir(CHROMA_PATH)
    if _CHROMA_CLIENT is None:
        _CHROMA_CLIENT = chromadb.PersistentClient(path=str(CHROMA_PATH))
    
    _MEM_COLLECTION = _CHROMA_CLIENT.get_or_create_collection(
        name="document_memory",
        embedding_function=NagrikEmbeddingFunction(),
        metadata={"hnsw:space": "cosine"}
    )
    return _MEM_COLLECTION

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

def index_document_chunks(job_id: str, filename: str, pages: list[dict[str, Any]]) -> None:
    """Chunks each page paragraph-by-paragraph and indexes into ChromaDB with context."""
    collection = _get_memory_collection()
    
    ids = []
    documents = []
    metadatas = []
    
    for page in pages:
        page_num = page.get("page", 0)
        markdown = page.get("markdown", "")
        # Paragraph-level chunking
        paragraphs = [p.strip() for p in markdown.split("\n\n") if p.strip()]
        
        for i, para in enumerate(paragraphs):
            # Deterministic but unique ID
            chunk_id = f"{job_id}_p{page_num}_c{i}"
            
            # Contextual Injection: Prepend metadata to help semantic matching identify the doc
            # This helps matching "Passport of John" to a chunk in passport.pdf
            enriched_text = f"[Source: {filename}, Page: {page_num + 1}]\n{para}"
            
            ids.append(chunk_id)
            documents.append(enriched_text)
            metadatas.append({
                "job_id": job_id,
                "filename": filename,
                "page": page_num,
                "chunk_index": i,
                "raw_text": para # Keep original for display
            })
            
    if ids:
        collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )
        logger.info(f"[Nagrik] Indexed {len(ids)} document chunks for Memory.")

def search_document_memory(query: str, n_results: int = 5) -> list[dict[str, Any]]:
    """Cross-document semantic search with Keyword Boosting and LLM Reranking."""
    collection = _get_memory_collection()
    
    # Retrieve more candidates than we need to allow for reranking
    search_n = 15
    res = collection.query(
        query_texts=[query],
        n_results=search_n
    )
    
    hits = []
    if res["ids"] and res["ids"][0]:
        query_tokens = set(query.lower().split())
        
        for i in range(len(res["ids"][0])):
            distance = res["distances"][0][i]
            meta = res["metadatas"][0][i]
            raw_text = meta.get("raw_text") or res["documents"][0][i]
            
            # Case-insensitive keyword boosting for multi-language support (English/Hindi)
            text_lower = raw_text.lower()
            overlap_count = sum(1 for token in query_tokens if token in text_lower)
            boost = (overlap_count / max(1, len(query_tokens))) * 0.2
            
            # cosine distance: 0.0 is exact match, 1.0 is opposite
            # Final score = semantic_score + keyword_boost
            score = max(0.0, 1.0 - distance) + boost
            
            hits.append({
                "score": round(score, 3),
                "text": raw_text,
                "filename": meta.get("filename"),
                "page": meta.get("page"),
                "job_id": meta.get("job_id")
            })
    
    # Sort by improved heuristic score
    hits.sort(key=lambda x: x["score"], reverse=True)
    
    # LLM Reranking Step: Refine the top 10
    top_candidates = hits[:10]
    if top_candidates:
        try:
            reranked = rerank_memory_results(query, top_candidates, top_k=n_results)
            return reranked
        except Exception as e:
            logger.error(f"Reranking failed: {e}")
            return hits[:n_results]
            
    return hits[:n_results]

def clear_memory_for_job(job_id: str):
    """Deletes all chunks belonging to a specific job ID."""
    collection = _get_memory_collection()
    try:
        collection.delete(where={"job_id": job_id})
        logger.info(f"[Nagrik] Deleted memory vectors for {job_id}")
    except Exception as e:
        logger.error(f"[Nagrik] Failed to delete memory for {job_id}: {e}")

def clear_memory_for_user(user_id: str):
    """
    Purges all memory. For this prototype, we clear everything to ensure 
    privacy on leave, matching our 'Session-Ephemeral' policy.
    """
    collection = _get_memory_collection()
    try:
        # Currently, since we don't have separate collections per user, 
        # we clear the entire collection to honor the 'Wipe on Logout' policy.
        # In a multi-user production system, we would filter by user_id.
        count = collection.count()
        if count > 0:
            # Note: ChromaDB 0.4+ delete() with no filters deletes according to collection logic.
            # We can also get all IDs and delete them.
            results = collection.get()
            if results["ids"]:
                collection.delete(ids=results["ids"])
            logger.info(f"[Nagrik] Memory cache for {user_id} cleared ({count} items).")
    except Exception as e:
        logger.error(f"[Nagrik] Failed to clear user memory: {e}")
