from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field

class PageClassification(str, Enum):
    FORM_INSTRUCTIONS = "form_instructions"
    DECLARATION_PAGE = "declaration_page"
    IDENTITY_SECTION = "identity_section"
    SIGNATURE_PAGE = "signature_page"
    TABLE_PAGE = "table_page"
    MIXED_PAGE = "mixed_page"
    UNKNOWN = "unknown"

class SimplificationLevel(int, Enum):
    LITERAL = 1       # Accurate translation, keep technical terms
    SIMPLE = 2        # Simple language, short sentences (default)
    ULTRA_BASIC = 3   # 5-word sentences, voice-first, rural-accessible

class BoundingBox(BaseModel):
    x: float = Field(0.0, description="X coordinate (top-left).")
    y: float = Field(0.0, description="Y coordinate (top-left).")
    width: float = Field(0.0, description="Width of the box.")
    height: float = Field(0.0, description="Height of the box.")
    page: int = Field(0, description="Page number this box belongs to.")

class DetectedField(BaseModel):
    label: str = Field(..., description="Field label detected from OCR layout.")
    pattern_type: str = Field(..., description="How it was detected: label_blank, checkbox, table_cell, etc.")
    line_number: int = Field(0, description="Line number in the OCR markdown.")
    value_hint: str = Field("", description="Any pre-filled value detected alongside the label.")

class FieldCandidate(BaseModel):
    field_name: str = Field(..., description="The name or label of the field.")
    what_to_fill: str = Field(..., description="Actionable instruction on what the user must write.")
    why_it_matters: str = Field(..., description="Brief reason why this field is important.")
    example: str = Field("", description="A local context example of what answers look like.")
    source: str = Field("document_text", description="Citation: guideline title used, 'detected_from_form', or 'document_text'.")
    retrieval_score: Optional[float] = Field(None, description="Internal RAG confidence score for the primary hit.")
    bbox: Optional[BoundingBox] = Field(None, description="Bounding box for visual grounding on the document image.")

class PageOutput(BaseModel):
    language: str = Field("English", description="The language the text is written in.")
    page_type: str = Field("unknown", description="The classified type of the page.")
    document_purpose: str = Field("Document", description="What this document is used for overall.")
    page_summary: str = Field("Page analysis", description="The purpose of this specific page in simple terms.")
    translation: str = Field("", description="A direct translation of the page's original main text.")
    simple_explanation: str = Field("", description="A plain-language explanation of what it means.")
    action_guide: str = Field("", description="Steps the user needs to take.")
    fields: List[FieldCandidate] = Field(default_factory=list, description="Form fields the user needs to fill out.")
    warnings: List[str] = Field(default_factory=list, description="Key warnings or requirements (e.g. mandatory signatures).")
    original_markdown: str = Field("", description="The original OCR markdown for context.")
    field_retrievals: Optional[dict] = Field(None, description="Internal mapping of field names to retrieved context for grounding.")
    retrieved_guidelines: List[str] = Field(default_factory=list, description="Titles of civic guidelines retrieved for this page.")
    confidence: float = Field(default=1.0, description="Value from 0.0 to 1.0 indicating AI confidence.")


class VerificationResult(BaseModel):
    passed: bool
    reason: Optional[str] = None
