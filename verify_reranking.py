import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parent))

from backend.llm import rerank_memory_results
from backend.rag import search_document_memory

def test_reranking():
    print("--- Testing Reranking Logic ---")
    query = "Where does Shresth live?"
    hits = [
        {"text": "John Doe is a lawyer.", "filename": "test.txt", "page": 0},
        {"text": "Shresth lives in Rampur.", "filename": "test.txt", "page": 0},
        {"text": "Rampur is famous for mangoes.", "filename": "test.txt", "page": 0},
    ]
    
    # Test Reranking
    reranked = rerank_memory_results(query, hits, top_k=2)
    print("\nQuery:", query)
    print("Reranked Output:")
    for h in reranked:
        print(f" - {h['text']}")
    
    if "Rampur" in reranked[0]["text"]:
        print("\nSUCCESS: Correct result ranked first.")
    else:
        print("\nFAILURE: Reranking did not prioritize correctly.")

def test_search_integration():
    print("\n--- Testing Search Integration (Mocked) ---")
    # This will check if keyword boosting is working in search_document_memory
    # Note: Requires uvicorn/backend state to be realistic, but we can call functions directly.
    query = "mangoes"
    hits = search_document_memory(query, n_results=3)
    
    print("\nQuery:", query)
    for h in hits:
        print(f" - Score: {h['score']} | {h['text'][:50]}...")

if __name__ == "__main__":
    try:
        test_reranking()
        # test_search_integration() # Skip unless DB is populated
    except Exception as e:
        print(f"Error during verification: {e}")
