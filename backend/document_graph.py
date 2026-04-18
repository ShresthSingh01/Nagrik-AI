from __future__ import annotations
import hashlib
import re
from dataclasses import dataclass, field
from typing import Any, List, Optional

from .utils import HEADING_RE, markdown_to_plain_text, first_heading

@dataclass
class GraphNode:
    node_id: str
    page: int
    title: str
    content: str
    level: int = 0
    parent_id: Optional[str] = None
    next_sibling_id: Optional[str] = None
    prev_sibling_id: Optional[str] = None
    continued_from_id: Optional[str] = None
    continues_to_id: Optional[str] = None
    table_headers: Optional[List[str]] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_id": self.node_id,
            "page": self.page,
            "title": self.title,
            "content": self.content,
            "level": self.level,
            "parent_id": self.parent_id,
            "next_sibling_id": self.next_sibling_id,
            "prev_sibling_id": self.prev_sibling_id,
            "continued_from_id": self.continued_from_id,
            "continues_to_id": self.continues_to_id,
            "table_headers": self.table_headers,
            "metadata": self.metadata
        }

class DocumentGraph:
    def __init__(self):
        self.nodes: dict[str, GraphNode] = {}
        self.root_id: Optional[str] = None

    def _generate_id(self, content: str, page: int, index: int) -> str:
        base = f"p{page}_i{index}_{content[:20]}"
        return hashlib.md5(base.encode()).hexdigest()[:12]

    def build(self, pages: List[dict[str, Any]]):
        """Builds a structural graph from OCR pages."""
        last_node_by_level: dict[int, str] = {}
        
        # 1. Create Root Node
        doc_title = pages[0].get("filename", "Document") if pages else "Document"
        root = GraphNode(
            node_id="root",
            page=0,
            title=doc_title,
            content="",
            level=0
        )
        self.nodes["root"] = root
        self.root_id = "root"
        last_node_by_level[0] = "root"

        for p_idx, page in enumerate(pages):
            page_num = int(page.get("page", 0))
            markdown = page.get("markdown") or ""
            blocks = page.get("blocks", [])
            
            # Simplified: Use markdown headers to split sections
            lines = markdown.splitlines()
            current_section_title = first_heading(markdown)
            current_section_content = []
            
            # We treat Each Page as a Level 1 container if no headers exist, 
            # otherwise we follow the header levels.
            
            sections = self._split_markdown_to_sections(markdown)
            
            page_node_id = f"page_{page_num}"
            page_node = GraphNode(
                node_id=page_node_id,
                page=page_num,
                title=f"Page {page_num}",
                content=markdown_to_plain_text(markdown),
                level=1,
                parent_id="root"
            )
            self.nodes[page_node_id] = page_node
            
            # Link to previous page
            if page_num > 1:
                prev_page_id = f"page_{page_num-1}"
                if prev_page_id in self.nodes:
                    self.nodes[prev_page_id].next_sibling_id = page_node_id
                    page_node.prev_sibling_id = prev_page_id

            # Add sub-sections
            prev_s_id = None
            for s_idx, (title, content, level) in enumerate(sections):
                s_id = self._generate_id(content, page_num, s_idx)
                
                # Table Header Detection
                headers = None
                if "| " in content and "---" in content:
                    lines = content.splitlines()
                    for line in lines:
                        if "|" in line and "---" not in line:
                            headers = [c.strip() for c in line.split("|") if c.strip()]
                            break

                node = GraphNode(
                    node_id=s_id,
                    page=page_num,
                    title=title,
                    content=content,
                    level=level + 1, # +1 because root is 0, page is 1
                    parent_id=page_node_id,
                    table_headers=headers
                )
                
                # Section Continuation Detection (Simple heuristic)
                if prev_s_id is None and page_num > 1:
                    # Check if this first section of page N continues the last section of page N-1
                    prev_page_id = f"page_{page_num-1}"
                    # Find last child of prev page
                    last_child_id = None
                    for nid, nnode in self.nodes.items():
                        if nnode.parent_id == prev_page_id:
                            last_child_id = nid # This is not perfect as dict order might vary, but for MVP...
                    
                    if last_child_id:
                        prev_node = self.nodes[last_child_id]
                        # If titles are similar or content ends abruptly
                        if prev_node.title == node.title:
                            node.continued_from_id = last_child_id
                            prev_node.continues_to_id = s_id

                if prev_s_id:
                    self.nodes[prev_s_id].next_sibling_id = s_id
                    node.prev_sibling_id = prev_s_id
                
                self.nodes[s_id] = node
                prev_s_id = s_id

    def _split_markdown_to_sections(self, markdown: str) -> List[tuple[str, str, int]]:
        lines = markdown.splitlines()
        sections = []
        curr_title = "Intro"
        curr_level = 1
        curr_lines = []
        
        for line in lines:
            m = HEADING_RE.match(line)
            if m:
                if curr_lines:
                    sections.append((curr_title, "\n".join(curr_lines).strip(), curr_level))
                curr_level = len(m.group(1))
                curr_title = m.group(2).strip()
                curr_lines = []
            else:
                curr_lines.append(line)
        
        if curr_lines or curr_title:
            sections.append((curr_title, "\n".join(curr_lines).strip(), curr_level))
            
        return sections

    def get_context(self, node_id: str, depth: int = 1) -> str:
        """Retrieves content with expanded structural context."""
        if node_id not in self.nodes:
            return ""
        
        node = self.nodes[node_id]
        context_parts = []
        
        # 1. Parent context (Heading hierarchy)
        curr_p = node.parent_id
        while curr_p and curr_p in self.nodes:
            p_node = self.nodes[curr_p]
            if p_node.level > 0:
                context_parts.insert(0, f"[Section: {p_node.title}]")
            curr_p = p_node.parent_id
            
        # 2. Previous context (if continuation)
        if node.continued_from_id and node.continued_from_id in self.nodes:
            prev_node = self.nodes[node.continued_from_id]
            context_parts.append(f"--- Continued from Page {prev_node.page} ---")
            context_parts.append(prev_node.content[-500:]) # Last 500 chars
            
        # 3. Target content
        context_parts.append(f"--- Content (Page {node.page}) ---")
        
        # Table Header Injection
        if node.table_headers:
            context_parts.append(f"[Table Headers: {', '.join(node.table_headers)}]")
        
        context_parts.append(node.content)
        
        # 4. Next context (if continuation)
        if node.continues_to_id and node.continues_to_id in self.nodes:
            next_node = self.nodes[node.continues_to_id]
            context_parts.append(f"--- Continues on Page {next_node.page} ---")
            context_parts.append(next_node.content[:500]) # First 500 chars
            
        return "\n".join(context_parts)

    def search(self, query: str, limit: int = 3) -> List[str]:
        """Simple keyword search across nodes to find starting points."""
        from .utils import score_overlap
        scored = []
        for nid, node in self.nodes.items():
            if node.level == 0: continue
            score = score_overlap(query, f"{node.title} {node.content}")
            if score > 0:
                scored.append((score, nid))
        
        scored.sort(key=lambda x: x[0], reverse=True)
        return [self.get_context(nid) for _, nid in scored[:limit]]
