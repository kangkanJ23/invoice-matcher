from pydantic import BaseModel
from typing import Optional, List


# -----------------------------------------------------
# Document Upload DTO
# -----------------------------------------------------
class DocumentUploadDTO(BaseModel):
    company_id: int
    doc_type: str   # "PO" | "INVOICE" | "DELIVERY"


# -----------------------------------------------------
# OCR + Parse Output DTO
# -----------------------------------------------------
class ParsedDocumentDTO(BaseModel):
    ocr_text: str
    parsed: Optional[dict] = None


# -----------------------------------------------------
# Match Request DTO
# -----------------------------------------------------
class MatchRequestDTO(BaseModel):
    company_id: int
    po_id: int
    invoice_id: int


# -----------------------------------------------------
# Match Result DTO
# -----------------------------------------------------
class MatchResultDTO(BaseModel):
    mismatches: List[dict]
    fraud_flags: List[str]
    score: float
