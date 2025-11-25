from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


# ------------------------------
# Company Table
# ------------------------------
class Company(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    contact_person: Optional[str] = None
    email: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ------------------------------
# Document Table
# ------------------------------
class Document(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    company_id: Optional[int] = Field(default=None, foreign_key="company.id")
    filename: str
    doc_type: str                          # PO / INVOICE / DELIVERY
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)

    # OCR + parsed output (store as TEXT/JSON)
    ocr_text: Optional[str] = None
    parsed_json: Optional[str] = None


# ------------------------------
# Match Table
# ------------------------------
class Match(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    company_id: Optional[int] = Field(default=None, foreign_key="company.id")
    po_id: Optional[int] = Field(default=None, foreign_key="document.id")
    invoice_id: Optional[int] = Field(default=None, foreign_key="document.id")

    status: Optional[str] = None            # Matched / Warning / Failed
    mismatches: Optional[str] = None        # JSON string
    fraud_flags: Optional[str] = None       # JSON string
    confidence_score: Optional[float] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
