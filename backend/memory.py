"""
Lightweight Document Memory.

Accumulates important facts from all pages AFTER parallel processing,
then does a single cheap post-pass to inject cross-page references.
This keeps parallel processing intact (80% benefit, 20% cost).
"""
from __future__ import annotations  # future compatibility ke liye (type hints cleaner ho jate hain)

import re  # regex operations ke liye
from typing import Any  # generic type support

# Fields jo usually har page me repeat hote hain (important identity info)
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
    # Label ko clean karna: lowercase + special characters hatao
    return re.sub(r"[^a-z0-9 ]", "", label.lower()).strip()


class DocumentMemory:
    """Collects facts from all pages and detects cross-page repetitions."""

    def __init__(self):
        # Yeh dict store karega normalized key -> uska data
        self.facts: dict[str, dict[str, Any]] = {}
        # format: key -> {"value": "...", "first_page": 1, "label": "Applicant Name"}

    def absorb_page(self, page_num: int, page_output: dict[str, Any]) -> None:
        """Ek page se important key-value data extract karta hai."""
        for field in page_output.get("fields", []):
            label = field.get("field_name", "")  # field ka naam
            norm = _normalize_key(label)  # normalize karke compare karenge
            if not norm:
                continue  # agar empty hai toh skip

            # Check karo kya yeh field repeatable category me aata hai
            matched = False
            for rk in REPEATABLE_KEYS:
                if rk in norm or norm in rk:  # loose matching (smart but imperfect)
                    matched = True
                    break

            # Agar match hua aur pehle se store nahi hai tabhi save karo
            if matched and norm not in self.facts:
                example = field.get("example", "")  # sample value
                self.facts[norm] = {
                    "value": example,
                    "first_page": page_num,
                    "label": label,
                }

    def enrich_pages(self, page_results: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Final pass: sab pages ko scan karke detect karta hai
        ki koi field pehle kisi aur page me fill ho chuka hai ya nahi.
        Agar haan, toh hint add karta hai.
        """

        # Step 1: Sab pages ka data collect karo
        for result in page_results:
            self.absorb_page(result.get("page", 0), result)

        # Step 2: Har page ko enrich karo (cross reference add karo)
        for result in page_results:
            current_page = result.get("page", 0)

            for field in result.get("fields", []):
                label = field.get("field_name", "")
                norm = _normalize_key(label)

                # Check karo kya yeh repeatable field hai
                for rk in REPEATABLE_KEYS:
                    if rk in norm or norm in rk:
                        # Fact lookup: exact ya normalized key se
                        fact = self.facts.get(rk) or self.facts.get(norm)

                        # Agar same field pehle page pe exist karta hai
                        if fact and fact["first_page"] != current_page and fact["first_page"] < current_page:
                            hint = f"Same as '{fact['label']}' on Page {fact['first_page']}"

                            # Agar example value hai toh usko bhi hint me dikhado
                            if fact["value"]:
                                hint += f" (e.g. \"{fact['value']}\")"

                            # Existing instruction ke sath merge karo
                            existing = field.get("what_to_fill", "")

                            # Duplicate hint add na ho
                            if hint not in existing:
                                field["what_to_fill"] = f"{existing}. {hint}".strip(". ")

                        break  # ek baar match ho gaya toh aur check nahi karna

        return page_results  # final enriched output