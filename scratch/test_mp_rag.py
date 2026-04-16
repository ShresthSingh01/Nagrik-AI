import sys
import os
import asyncio

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.rag import load_guidelines, _hybrid_search

async def test_mp_rag():
    test_queries = [
        "What is Samagra ID?",
        "How to apply for Ladli Behna?",
        "Is affidavit needed for domicile in MP?",
        "Where to register for wheat procurement?",
        "Jan kalyan sambal yojana rules"
    ]
    
    # Load guidelines first
    guidelines = load_guidelines()
    
    print("--- NagrikAI MP RAG Verification ---\n")
    for q in test_queries:
        print(f"User Query: {q}")
        hits = _hybrid_search(q, guidelines, limit=1)
        if hits:
            res = hits[0]['guideline']
            print(f"Match: {res['title']}")
            print(f"Score: {hits[0].get('score', 'N/A')}")
            print(f"Guidance Snippet: {res.get('what_to_ask_user', '')[:100]}...")
        else:
            print("❌ No match found!")
        print("-" * 20)

if __name__ == "__main__":
    asyncio.run(test_mp_rag())
