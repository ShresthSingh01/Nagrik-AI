"""
Error Prevention Layer.

Rule-based validators for common Indian civic form fields.
Zero LLM calls — pure pattern matching.
Generates user-facing warnings to prevent submission errors.
"""
from __future__ import annotations

import re
from typing import Any

VALIDATION_RULES: list[dict[str, Any]] = [
    {
        "keywords": ["aadhar", "aadhaar", "uid", "uidai"],
        "message": "Aadhar number must be exactly 12 digits (e.g. 1234 5678 9012).",
        "format_hint": "XXXX XXXX XXXX",
    },
    {
        "keywords": ["phone", "mobile", "contact number", "mobile number", "telephone"],
        "message": "Phone number must be exactly 10 digits starting with 6-9.",
        "format_hint": "98XXXXXXXX",
    },
    {
        "keywords": ["pin", "pincode", "pin code", "postal code", "zip"],
        "message": "PIN code must be exactly 6 digits.",
        "format_hint": "XXXXXX",
    },
    {
        "keywords": ["date of birth", "dob", "birth date"],
        "message": "Date must be in DD/MM/YYYY format (e.g. 15/08/1990).",
        "format_hint": "DD/MM/YYYY",
    },
    {
        "keywords": ["email", "e-mail", "email address"],
        "message": "Enter a valid email address (e.g. name@example.com).",
        "format_hint": "name@example.com",
    },
    {
        "keywords": ["pan", "pan number", "pan card"],
        "message": "PAN must be 10 characters: 5 letters, 4 digits, 1 letter (e.g. ABCDE1234F).",
        "format_hint": "ABCDE1234F",
    },
    {
        "keywords": ["ifsc", "ifsc code"],
        "message": "IFSC code must be 11 characters: 4 letters, 0, then 6 alphanumeric (e.g. SBIN0001234).",
        "format_hint": "XXXX0XXXXXX",
    },
    {
        "keywords": ["account", "account number", "bank account"],
        "message": "Bank account number is typically 9-18 digits. Double-check with your passbook.",
        "format_hint": "XXXXXXXXX to XXXXXXXXXXXXXXXXXX",
    },
    {
        "keywords": ["voter", "voter id", "epic"],
        "message": "Voter ID (EPIC) is typically 3 letters followed by 7 digits (e.g. ABC1234567).",
        "format_hint": "ABC1234567",
    },
    {
        "keywords": ["ration", "ration card"],
        "message": "Ration card number format varies by state. Check your physical card.",
        "format_hint": "State-specific",
    },
    {
        "keywords": ["signature", "sign", "thumb"],
        "message": "Signature must match your official records. Use thumb impression if unable to sign.",
        "format_hint": "",
    },
    {
        "keywords": ["photograph", "photo", "passport photo"],
        "message": "Photo must be recent, passport-sized (3.5cm x 4.5cm), with white background.",
        "format_hint": "3.5cm x 4.5cm",
    },
]


def validate_fields(fields: list[dict[str, Any]]) -> list[str]:
    """
    Check detected/generated fields against known format rules.
    Returns a list of user-facing warning strings.
    """
    warnings: list[str] = []
    seen_rules: set[int] = set()

    for field in fields:
        field_name = (field.get("field_name") or field.get("label") or "").lower()
        if not field_name:
            continue

        for rule_idx, rule in enumerate(VALIDATION_RULES):
            if rule_idx in seen_rules:
                continue
            for keyword in rule["keywords"]:
                if keyword in field_name:
                    warning = f"[WARNING] {field.get('field_name', field_name)}: {rule['message']}"
                    if rule["format_hint"]:
                        warning += f" Format: {rule['format_hint']}"
                    warnings.append(warning)
                    seen_rules.add(rule_idx)
                    break

    return warnings
