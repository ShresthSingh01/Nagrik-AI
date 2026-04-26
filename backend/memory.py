"""
Lightweight Document Memory.

Accumulates important facts from all pages AFTER parallel processing,
then does a single cheap post-pass to inject cross-page references.
This keeps parallel processing intact (80% benefit, 20% cost).
"""
from __future__ import annotations

import re
from typing import Any

# Fields that commonly repeat across pages
REPEATABLE_KEYS = {
    "name", "applicant name", "full name", "father", "father's name",
    "guardian", "guardian name", "mother", "mother's name",
    "address", "permanent address", "residential address",
    "aadhar", "aadhaar", "uid", "aadhar number",
    "phone", "mobile", "contact number", "mobile number",
    "date of birth", "dob", "pin", "pincode", "pin code",
    "email", "email address", "district", "state", "village",
}


def _normalize_key(label: str) -> str:
    return re.sub(r"[^a-z0-9 ]", "", label.lower()).strip()


class DocumentMemory:
    """Collects facts from all pages and detects cross-page repetitions."""

    def __init__(self):
        self.facts: dict[str, dict[str, Any]] = {}
        # key -> {"value": "...", "first_page": 1, "label": "Applicant Name"}

    def absorb_page(self, page_num: int, page_output: dict[str, Any]) -> None:
        """Extract key-value facts from a processed page."""
        for field in page_output.get("fields", []):
            label = field.get("field_name", "")
            norm = _normalize_key(label)
            if not norm:
                continue

            # Only track fields that are likely to repeat
            matched = False
            for rk in REPEATABLE_KEYS:
                if rk in norm or norm in rk:
                    matched = True
                    break

            if matched and norm not in self.facts:
                example = field.get("example", "")
                self.facts[norm] = {
                    "value": example,
                    "first_page": page_num,
                    "label": label,
                }

    def enrich_pages(self, page_results: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Post-pass: scan all pages for fields that reference data from earlier pages.
        Appends cross-page hints to the `warnings` list.
        """
        # First, absorb all pages
        for result in page_results:
            self.absorb_page(result.get("page", 0), result)

        # Then, enrich each page
        for result in page_results:
            current_page = result.get("page", 0)
            for field in result.get("fields", []):
                label = field.get("field_name", "")
                norm = _normalize_key(label)

                for rk in REPEATABLE_KEYS:
                    if rk in norm or norm in rk:
                        fact = self.facts.get(rk) or self.facts.get(norm)
                        if fact and fact["first_page"] != current_page and fact["first_page"] < current_page:
                            hint = f"Same as '{fact['label']}' on Page {fact['first_page']}"
                            if fact["value"]:
                                hint += f" (e.g. \"{fact['value']}\")"
                            # Inject hint into the field
                            existing = field.get("what_to_fill", "")
                            if hint not in existing:
                                field["what_to_fill"] = f"{existing}. {hint}".strip(". ")
                        break

        return page_results
