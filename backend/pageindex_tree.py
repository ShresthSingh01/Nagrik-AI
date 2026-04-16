from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import re

from .utils import FIELD_RE, first_heading, markdown_to_plain_text, score_overlap

@dataclass
class TreeNode:
    page: int
    title: str
    text: str
    level: int = 0
    children: list["TreeNode"] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "page": self.page,
            "title": self.title,
            "text": self.text,
            "level": self.level,
            "children": [child.to_dict() for child in self.children],
        }

def _split_sections(markdown: str) -> list[tuple[str, str, int]]:
    lines = (markdown or "").splitlines()
    sections: list[tuple[str, str, int]] = []
    current_title = None
    current_level = 0
    current_buffer: list[str] = []

    def flush():
        nonlocal current_title, current_buffer, current_level
        if current_title is None:
            return
        sections.append((current_title, "\n".join(current_buffer).strip(), current_level))
        current_buffer = []

    for line in lines:
        m = re.match(r"^(#{1,6})\s+(.*)$", line.strip())
        if m:
            flush()
            current_title = m.group(2).strip()
            current_level = len(m.group(1))
        else:
            current_buffer.append(line)
    if current_title is None:
        sections.append((first_heading(markdown), markdown or "", 1))
    else:
        flush()
    cleaned: list[tuple[str, str, int]] = []
    for title, txt, level in sections:
        plain = markdown_to_plain_text(txt)
        if plain:
            cleaned.append((title, plain, level))
    return cleaned or [(first_heading(markdown), markdown_to_plain_text(markdown), 1)]

def build_pageindex_tree(pages: list[dict[str, Any]]) -> dict[str, Any]:
    root = TreeNode(page=0, title="root", text="", level=0)
    for page in pages:
        page_num = int(page.get("page", 0))
        markdown = page.get("markdown") or ""
        sections = _split_sections(markdown)
        page_title = first_heading(markdown)
        page_node = TreeNode(page=page_num, title=page_title, text=markdown_to_plain_text(markdown), level=1)
        for title, text, level in sections:
            page_node.children.append(TreeNode(page=page_num, title=title, text=text, level=level))
        root.children.append(page_node)
    return root.to_dict()

def flatten_tree(tree: dict[str, Any]) -> list[dict[str, Any]]:
    nodes: list[dict[str, Any]] = []
    def walk(node: dict[str, Any]):
        if node.get("page", 0):
            nodes.append(node)
        for child in node.get("children", []):
            walk(child)
    walk(tree)
    return nodes

def extract_field_candidates(pages: list[dict[str, Any]]) -> dict[int, list[str]]:
    out: dict[int, list[str]] = {}
    letter_re = re.compile(r"[A-Za-z\u0900-\u097F]")
    marker_re = re.compile(r"^\s*(?:\(?\d{1,3}[.)]|[A-Za-z\u0900-\u097F][.)]|[•·*]+)\s*")
    noise = {
        "note", "notes", "example", "yes", "no", "हाँ", "नहीं",
        "affiliated to", "approved by", "circular", "date", "naac",
    }

    def normalize_label(text: str) -> str:
        cleaned = re.sub(r"[#*_`|]", " ", text or "")
        cleaned = marker_re.sub("", cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned).strip(" :-–—")
        return cleaned

    def valid_label(text: str) -> bool:
        if not text or len(text) < 2 or len(text) > 120:
            return False
        if not letter_re.search(text):
            return False
        compact = text.replace(" ", "")
        if re.match(r"^[A-Za-z0-9/._-]{2,24}$", compact) and re.search(r"[0-9/]", compact):
            return False
        digit_count = sum(ch.isdigit() for ch in text)
        if digit_count > 0 and digit_count / max(1, len(text)) > 0.25:
            return False
        if text.lower() in noise:
            return False
        return True

    for page in pages:
        page_num = int(page.get("page", 0))
        markdown = page.get("markdown") or ""
        candidates: list[str] = []
        for raw_line in markdown.splitlines():
            line = raw_line.strip()
            if not line:
                continue

            if line.startswith("|") and line.endswith("|"):
                cells = [normalize_label(c) for c in line.strip("|").split("|")]
                for cell in cells:
                    if valid_label(cell):
                        candidates.append(cell)
                continue

            m = FIELD_RE.match(line)
            if m:
                label = normalize_label(m.group(1))
                if valid_label(label):
                    candidates.append(label)
            if re.search(r"[_\.]{3,}\s*$", line):
                label = normalize_label(re.sub(r"[_\.]{3,}\s*$", "", line))
                if valid_label(label):
                    candidates.append(label)
        if candidates:
            deduped: list[str] = []
            seen: set[str] = set()
            for item in candidates:
                key = item.lower()
                if key not in seen:
                    seen.add(key)
                    deduped.append(item)
            out[page_num] = deduped
    return out

def best_tree_nodes(query: str, tree: dict[str, Any], page_num: int | None = None, limit: int = 3) -> list[dict[str, Any]]:
    nodes = flatten_tree(tree)
    scored: list[tuple[float, dict[str, Any]]] = []
    for node in nodes:
        text = f"{node.get('title', '')} {node.get('text', '')}"
        score = score_overlap(query, text)
        if page_num is not None and int(node.get("page", -1)) == int(page_num):
            score += 0.20
        if node.get("level", 99) <= 2:
            score += 0.05
        if score > 0:
            scored.append((score, node))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [node for _, node in scored[:limit]]
