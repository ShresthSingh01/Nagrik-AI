from __future__ import annotations

from pathlib import Path
from typing import Any

from .config import settings
from .pageindex_tree import best_tree_nodes
from .utils import safe_read_json, score_overlap, get_embedding, cosine_similarity

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "civic_guidelines.json"

_CACHED_GUIDELINES: list[dict[str, Any]] | None = None

def prefetch_guideline_embeddings(guidelines: list[dict[str, Any]]):
    """Fetch all missing embeddings for guidelines in a single batch."""
    to_fetch = [item for item in guidelines if not item.get("_embedding")]
    if not to_fetch:
        return
    
    print(f"[Nagrik] Batch fetching {len(to_fetch)} guideline embeddings...")
    texts = [item["_text_blob"] for item in to_fetch]
    embeddings = get_embedding(texts)
    
    if embeddings and isinstance(embeddings, list) and len(embeddings) == len(to_fetch):
        for item, emb in zip(to_fetch, embeddings):
            item["_embedding"] = emb
        print(f"[Nagrik] Successfully pre-embedded {len(to_fetch)} items.")
    else:
        print("[Nagrik] Batch embedding failed, will fall back to lazy fetching.")

def load_guidelines() -> list[dict[str, Any]]:
    global _CACHED_GUIDELINES
    if _CACHED_GUIDELINES is not None:
        return _CACHED_GUIDELINES
    
    data = safe_read_json(DATA_PATH, default=[])
    guidelines = data if isinstance(data, list) else []
    
    # Initialize metadata
    for item in guidelines:
        item["_text_blob"] = " ".join([
            str(item.get("title", "")),
            " ".join(item.get("keywords", []) if isinstance(item.get("keywords"), list) else []),
            str(item.get("description", ""))
        ])
        if "_embedding" not in item:
            item["_embedding"] = None
        
    # Trigger prefetch (this is now batch-optimized)
    prefetch_guideline_embeddings(guidelines)
        
    _CACHED_GUIDELINES = guidelines
    return guidelines

def _hybrid_search(query: str, guidelines: list[dict[str, Any]], limit: int, skip_embedding: bool = False) -> list[dict[str, Any]]:
    """Returns a list of dicts with score included: {'score': float, 'guideline': dict}"""
    query_emb = get_embedding(query) if not skip_embedding else None
    
    scored = []
    for item in guidelines:
        # Keyword score (0.0 to 1.0)
        kw_score = score_overlap(query, item.get("_text_blob", ""))
        
        # Semantic score (Lazy fetch)
        sem_score = 0.0
        if query_emb:
            if item.get("_embedding") is None:
                item["_embedding"] = get_embedding(item["_text_blob"])
            
            if item["_embedding"]:
                sem_score = cosine_similarity(query_emb, item["_embedding"])
                sem_score = max(0.0, sem_score)
            
        # Hybrid score: if skip_embedding, we rely 100% on keywords
        if skip_embedding:
            final_score = kw_score
        else:
            final_score = (sem_score * 0.7) + (kw_score * 0.3)
            
        if final_score > 0.1: # threshold
            scored.append({
                "score": round(final_score, 3),
                "guideline": item
            })
            
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:limit]

def retrieve_field_context(field_label: str, guidelines: list[dict[str, Any]], skip_embedding: bool = False) -> dict[str, Any] | None:
    """Finds the single best guideline for a specific field label."""
    hits = _hybrid_search(field_label, guidelines, limit=1, skip_embedding=skip_embedding)
    return hits[0] if hits else None

def retrieve_field_context_batch(field_labels: list[str], guidelines: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """
    Highly optimized batch RAG for many fields. 
    Reduces N API calls to 1 API call.
    """
    if not field_labels:
        return {}
    
    unique_labels = list(set(field_labels))
    # Step 1: Batch fetch embeddings for all labels in ONE call
    label_embeddings = get_embedding(unique_labels)
    
    # Map label -> embedding
    emb_map = {}
    if label_embeddings and isinstance(label_embeddings, list) and len(label_embeddings) == len(unique_labels):
        emb_map = dict(zip(unique_labels, label_embeddings))
    
    # Step 2: Local similarity search (zero API calls here)
    results = {}
    for label in field_labels:
        label_emb = emb_map.get(label)
        best_hit = None
        best_score = -1.0
        
        for item in guidelines:
            # Keyword score
            kw_score = score_overlap(label, item.get("_text_blob", ""))
            
            # Semantic score
            sem_score = 0.0
            if label_emb and item.get("_embedding"):
                sem_score = cosine_similarity(label_emb, item["_embedding"])
                sem_score = max(0.0, sem_score)
            
            final_score = (sem_score * 0.7) + (kw_score * 0.3)
            if final_score > 0.2 and final_score > best_score:
                best_score = final_score
                best_hit = {
                    "score": round(final_score, 3),
                    "guideline": item
                }
        
        if best_hit:
            results[label] = best_hit
            
    return results

def retrieve_document_context(tree: dict[str, Any], guidelines: list[dict[str, Any]], skip_embedding: bool = False) -> dict[str, Any]:
    # Document level query is usually derived from the top level tree node
    root_title = tree.get("title", "")
    return {
        "guideline_hits": _hybrid_search(root_title, guidelines, limit=2, skip_embedding=skip_embedding)
    }

def retrieve_context(query: str, tree: dict[str, Any], guidelines: list[dict[str, Any]], page_num: int | None = None, skip_embedding: bool = False) -> dict[str, Any]:
    tree_hits = best_tree_nodes(query, tree, page_num=page_num, limit=settings.max_context_nodes)
    
    # Field level / localized context
    guideline_hits = _hybrid_search(query, guidelines, limit=settings.max_guideline_hits, skip_embedding=skip_embedding)
    
    return {
        "tree_hits": tree_hits,
        "guideline_hits": guideline_hits,
    }

