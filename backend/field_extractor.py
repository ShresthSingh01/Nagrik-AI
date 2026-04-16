"""
Rule-based field extractor.

Detects form fields from OCR markdown using deterministic patterns.
This runs BEFORE the LLM, so the LLM only explains fields — it doesn't discover them.
"""
from __future__ import annotations

import re
from typing import Any

# --- Patterns ---

LETTER_RE = re.compile(r"[A-Za-z\u0900-\u097F]")
LEADING_MARKER_RE = re.compile(r"^\s*(?:\(?\d{1,3}[.)]|[A-Za-z\u0900-\u097F][.)]|[•·*]+)\s*")

# Fragment regex for multi-field lines: "Label: value"
LABEL_VALUE_FRAG_RE = re.compile(
    r"([A-Za-z\u0900-\u097F][A-Za-z0-9\u0900-\u097F /().,'\-]{1,80})\s*[:：\-–—]\s*([^:：]+?)(?=\s{2,}[A-Za-z\u0900-\u097F]|$)",
)

# "Label: ______" or "Label: ___________"
LABEL_BLANK_RE = re.compile(
    r"\s*([A-Za-z\u0900-\u097F][A-Za-z0-9\u0900-\u097F /().,'\-]{1,120})\s*[:：\-–—]\s*[_\.]{3,}\s*",
)

# "[ ] Option text" or "[x] Option text" — checkbox
CHECKBOX_RE = re.compile(
    r"^\s*\[([xX ]?)\]\s*(.+)$",
)

# Line that ends with blanks (fill-in-the-blank)
TRAILING_BLANK_RE = re.compile(
    r"(.{5,80}?)\s*[_\.]{3,}\s*",
)

# Table row: "| cell | cell | cell |"
TABLE_ROW_RE = re.compile(
    r"^\s*\|(.+\|)+\s*$",
)

# Table separator: "| --- | --- |" or "|---|---|" or "| :--- | ---: |"
TABLE_SEP_RE = re.compile(
    r"^\s*\|[\s\-:]+(\|[\s\-:]+)*\|\s*$",
)

NOISE_LABELS = {
    "note", "notes", "example", "examples", "page", "sr", "sr no",
    "serial", "serial no", "sl", "sl no", "section", "part",
    "instructions", "instruction", "government of india",
    "affiliated to", "approved by", "circular", "date", "naac",
    "yes", "no", "ha", "nahi", "हाँ", "नहीं",
    # Indian Document Headers (Noise)
    "भाग", "अनुभाग", "अध्याय", "अनुबंध", "शपथ पत्र", "प्रमाण पत्र",
    "घोषणा", "हस्ताक्षर", "दिनांक", "स्थान", "कार्यालय",
    "form", "annexure", "appendix", "declaration", "affidavit",
    "signature", "office use", "official", "department",
    "application", "registration", "certificate", "ministry", "government",
    "form of", "scheme", "manual", "guideline", "notification",
    "प्रपत्र", "आवेदन", "योजना", "मंत्रालय", "सरकार", "पंजीकरण",
    "summary", "status", "version", "confidential",
    "undertaking", "oath", "agreement", "acknowledgment", "promise",
    "वचन", "शपथ", "सहमति", "करार", "स्वीकृति",
}


def _clean_label(label: str) -> str:
    """Strip markdown artifacts and normalize whitespace."""
    label = LEADING_MARKER_RE.sub("", label)
    label = re.sub(r"[#*_`]", "", label)
    label = re.sub(r"\s*[|]+\s*", " ", label)
    label = label.strip(" :-–—")
    label = re.sub(r"\s+", " ", label).strip()
    return label


def _looks_like_label(label: str) -> bool:
    if not label:
        return False
    # Labels usually aren't super long sentences
    if len(label) < 2 or len(label) > 100:
        return False
    if not LETTER_RE.search(label):
        return False
    
    # Check for too many spaces (indicates regular text, not a label)
    if label.count(" ") > 8:
        return False

    compact = label.replace(" ", "")
    if re.match(r"^[A-Za-z0-9/._-]{2,24}$", compact) and re.search(r"[0-9/]", compact):
        return False
    digit_count = sum(ch.isdigit() for ch in label)
    if digit_count > 0 and digit_count / max(1, len(label)) > 0.25:
        return False
    
    lowered = label.lower()
    if lowered in NOISE_LABELS:
        return False
    
    # Common heading prefix/keyword check
    noise_hints = ["application for", "form for", "certificate for", "scheme of", "department of", "ministry of", "government of"]
    if any(h in lowered for h in noise_hints):
        return False

    return True


def _append_field(
    fields: list[dict[str, Any]],
    seen: set[str],
    label: str,
    pattern_type: str,
    line_number: int,
    value_hint: str,
) -> None:
    clean = _clean_label(label)
    key = clean.lower()
    if not _looks_like_label(clean) or key in seen:
        return
    fields.append(
        {
            "label": clean,
            "pattern_type": pattern_type,
            "line_number": line_number,
            "value_hint": value_hint[:200],
        }
    )
    seen.add(key)


def _strip_markdown(line: str) -> str:
    """Remove markdown formatting artifacts that break field regex matching."""
    # Strip heading markers: # ## ### etc.
    s = re.sub(r"^#{1,6}\s+", "", line)
    # Strip bold/italic: **text** -> text, *text* -> text, __text__ -> text
    s = re.sub(r"\*\*(.+?)\*\*", r"\1", s)
    s = re.sub(r"\*(.+?)\*", r"\1", s)
    s = re.sub(r"__(.+?)__", r"\1", s)
    s = re.sub(r"_(.+?)_", r"\1", s)
    # Strip inline code: `text` -> text
    s = re.sub(r"`(.+?)`", r"\1", s)
    # Strip links: [text](url) -> text
    s = re.sub(r"\[(.+?)\]\(.+?\)", r"\1", s)
    return s.strip()


# Short standalone label pattern: e.g. "Name", "Father's Name", "नाम", "District"
# Require at least 2 characters to avoid catching single letters/noise
STANDALONE_LABEL_RE = re.compile(
    r"^\s*([A-Za-z\u0900-\u097F][A-Za-z0-9\u0900-\u097F /().,''\-]{2,60})\s*$",
)


def extract_fields_from_markdown(markdown: str) -> list[dict[str, Any]]:
    """
    Extract form field candidates from OCR markdown using layout heuristics.

    Returns a list of dicts:
        {
            "label": "Full Name",
            "pattern_type": "label_blank" | "label_value" | "checkbox" | "trailing_blank" | "table_cell",
            "line_number": 12,
            "value_hint": ""   # any value text detected alongside the label
        }
    """
    fields: list[dict[str, Any]] = []
    seen: set[str] = set()
    lines = (markdown or "").splitlines()

    i = 0
    while i < len(lines):
        raw_line = lines[i]
        line_no = i + 1
        line = raw_line.strip()
        if not line:
            i += 1
            continue

        # --- Pass 1: Table detection (header + rows) ---
        # Check against raw line first (preserves pipe characters)
        if (
            TABLE_ROW_RE.match(line)
            and i + 1 < len(lines)
            and TABLE_SEP_RE.match(lines[i + 1].strip())
        ):
            header_cells = [c.strip() for c in line.strip("|").split("|")]
            for cell in header_cells:
                _append_field(fields, seen, cell, "table_header", line_no, "")

            i += 2
            while i < len(lines):
                table_line = lines[i].strip()
                if not TABLE_ROW_RE.match(table_line):
                    break
                row_cells = [c.strip() for c in table_line.strip("|").split("|")]
                for cell in row_cells:
                    _append_field(fields, seen, cell, "table_cell", i + 1, "")
                i += 1
            continue

        # --- Strip markdown formatting for pattern matching ---
        clean_line = _strip_markdown(line)
        if not clean_line:
            i += 1
            continue

        # --- Pass 2: Line-level patterns (non-table) ---

        # --- Pass 2: Fragment-level patterns (non-table) ---

        # Multiple "Label: Value" fragments on one line
        frags = list(LABEL_VALUE_FRAG_RE.finditer(clean_line))
        if len(frags) > 1:
            for m in frags:
                _append_field(fields, seen, m.group(1), "label_value_multi", line_no, m.group(2).strip())
            i += 1
            continue

        # Checkbox: [ ] or [x]
        # (Handling multiple checkboxes on one line too)
        checkboxes = list(CHECKBOX_RE.finditer(clean_line))
        if checkboxes:
            for m in checkboxes:
                _append_field(
                    fields,
                    seen,
                    m.group(2),
                    "checkbox",
                    line_no,
                    "checked" if m.group(1).strip() else "",
                )
            i += 1
            continue

        # "Label: ______"
        m = LABEL_BLANK_RE.search(clean_line)
        if m:
            _append_field(fields, seen, m.group(1), "label_blank", line_no, "")
            # Don't skip line, there might be more fields if we use search
            # But the regex is currently broad. Let's just catch and continue Pass 2 checks
            # for other patterns if not anchored.
            
        # "Label: some value" (if finditer didn't catch multiple, try single match)
        if not frags:
            # Fallback for single label:value with potentially complex value
            m = re.search(r"^\s*([A-Za-z\u0900-\u097F][A-Za-z0-9\u0900-\u097F /().,'\-]{1,120})\s*[:：\-–—]\s*(.+)$", clean_line)
            if m:
                _append_field(fields, seen, m.group(1), "label_value", line_no, m.group(2).strip())
                i += 1
                continue

        # Trailing blanks: "Father's Name ________"
        m = TRAILING_BLANK_RE.search(clean_line)
        if m:
            _append_field(fields, seen, m.group(1), "trailing_blank", line_no, "")
            i += 1
            continue

        # --- Pass 3: Standalone short labels (common in Indian OCR) ---
        # Lines like "Name" or "पिता का नाम" that are short standalone labels
        # followed by a blank/fill line. Check next line for blank indicators.
        if i + 1 < len(lines):
            next_line = lines[i + 1].strip()
            next_is_blank_or_fill = (
                not next_line
                or re.match(r"^[_.\-–—\s]{3,}$", next_line)
                or next_line == "---"
            )
            if next_is_blank_or_fill:
                m = STANDALONE_LABEL_RE.match(clean_line)
                if m:
                    _append_field(fields, seen, m.group(1), "standalone_label", line_no, "")
                    i += 2  # skip the blank/fill line
                    continue

        i += 1

    return fields

