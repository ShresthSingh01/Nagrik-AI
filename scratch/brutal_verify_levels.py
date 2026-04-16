import sys
import os
import json
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from backend.llm import simplify_page
from backend.schema import SimplificationLevel

def brutal_test():
    print("---[ Brutal Level Verification ]---")
    
    # Real government form declaration snippet
    sample_text = """
    I, the undersigned, hereby declare that the particulars given above are true and correct to the best of my knowledge 
    and belief and I am aware that in the event of any information being found false or incorrect, 
    my candidature/application is liable to be rejected/cancelled and I may be liable for penal action 
    under the relevant sections of the Indian Penal Code.
    """
    
    results = {}
    
    for level in [SimplificationLevel.LITERAL, SimplificationLevel.SIMPLE, SimplificationLevel.ULTRA_BASIC]:
        print(f"Executing Mode: {level.name}...")
        output = simplify_page(
            language="English",
            page_num=1,
            page_markdown=sample_text,
            context={}, # No RAG needed for this tone test
            detected_fields=[],
            level=level
        )
        
        # We focus on the "simple_explanation" or "action_guide" to see the tone shift
        results[level.name] = {
            "summary": output.get("page_summary", ""),
            "explanation": output.get("simple_explanation", ""),
            "action": output.get("action_guide", ""),
            "fields": output.get("fields", [])
        }

    print("\n" + "="*80)
    print(f"{'LEVEL':<15} | {'SENTENCE LENGTH':<20} | {'PREVIEW'}")
    print("-" * 80)
    
    for name, data in results.items():
        text = data['explanation'] or data['summary']
        words = text.split()
        avg_len = len(words) # rough metric
        preview = text[:60] + "..."
        print(f"{name:<15} | {avg_len:<20} | {preview}")

    print("="*80 + "\n")
    
    # Save full JSON for inspection
    with open("scratch/level_comparison_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print("Full comparison saved to scratch/level_comparison_results.json")

if __name__ == "__main__":
    brutal_test()
