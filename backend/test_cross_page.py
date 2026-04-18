import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from backend.document_graph import DocumentGraph
from backend.session_memory import SessionMemory

def test_continuation_and_headers():
    pages = [
        {
            "page": 1,
            "markdown": "# Terms and Conditions\n1. First rule\n2. Second rule",
            "blocks": []
        },
        {
            "page": 2,
            "markdown": "# Terms and Conditions\n3. Third rule\n4. Fourth rule",
            "blocks": []
        },
        {
            "page": 3,
            "markdown": "# Table Data\n| Name | Age |\n|---|---|\n| John | 30 |",
            "blocks": []
        },
        {
            "page": 4,
            "markdown": "| Jane | 25 |",
            "blocks": []
        }
    ]
    
    graph = DocumentGraph()
    graph.build(pages)
    
    print("\n--- Verifying Document Graph ---")
    
    # Check if P2 intro node continues from P1 intro node
    p1_nodes = [nid for nid, n in graph.nodes.items() if n.page == 1 and n.title == "Terms and Conditions"]
    p2_nodes = [nid for nid, n in graph.nodes.items() if n.page == 2 and n.title == "Terms and Conditions"]
    
    if p1_nodes and p2_nodes:
        n1 = graph.nodes[p1_nodes[0]]
        n2 = graph.nodes[p2_nodes[0]]
        print(f"P1 Node ID: {n1.node_id}, Continues to: {n1.continues_to_id}")
        print(f"P2 Node ID: {n2.node_id}, Continued from: {n2.continued_from_id}")
        assert n1.continues_to_id == n2.node_id
        assert n2.continued_from_id == n1.node_id
        print("[PASS] Continuation linkage passed!")
    
    # Check if context expansion includes previous content
    context = graph.get_context(p2_nodes[0])
    print(f"\nExpanded Context for Page 2:\n{context}")
    assert "Continued from Page 1" in context
    assert "First rule" in context
    print("[PASS] Context expansion passed!")

    # Check session memory
    SessionMemory.update_session("test_sid", last_query="What are the rules?", last_answer="Rule 1 and 2.", cited_pages=[1])
    session_ctx = SessionMemory.get_context_for_llm("test_sid")
    print(f"\nSession Context:\n{session_ctx}")
    assert "Rule 1 and 2" in session_ctx
    print("[PASS] Session memory passed!")

if __name__ == "__main__":
    try:
        test_continuation_and_headers()
        print("\nALL TESTS PASSED")
    except Exception as e:
        print(f"\nTEST FAILED: {e}")
        import traceback
        traceback.print_exc()
