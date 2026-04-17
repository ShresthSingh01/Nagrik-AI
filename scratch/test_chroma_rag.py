import os
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from backend.rag import load_guidelines, retrieve_context
from backend.config import settings

def test_rag():
    print("Testing ChromaDB RAG...")
    
    if not os.getenv("MISTRAL_API_KEY"):
        print("Error: MISTRAL_API_KEY not set.")
        return

    # 1. Load guidelines (Should populate ChromaDB)
    guidelines = load_guidelines()
    print(f"Guidelines loaded: {len(guidelines)}")
    
    # 2. Test retrieval
    query = "aadhar card guidelines"
    print(f"Querying: '{query}'")
    
    # Dummy tree for context
    tree = {"title": "Test Document", "nodes": []}
    
    context = retrieve_context(query, tree, guidelines)
    
    print("\nResults:")
    for hit in context.get("guideline_hits", []):
        try:
            print(f"[{hit['score']}] {hit['guideline']['title']}")
            desc = hit['guideline']['description'][:100].replace('\u20b9', 'Rs.')
            print(f"   {desc}...")
        except UnicodeEncodeError:
            print(f"[{hit['score']}] (Encoding Error in Title)")


if __name__ == "__main__":
    test_rag()
