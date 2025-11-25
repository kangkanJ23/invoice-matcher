# backend/app/api/routes_documents.py
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, Query
from sqlmodel import Session, select
import json

from backend.app.db.session import get_session
from backend.app.db import crud
from backend.app.db.models import Document
from backend.app.schemas.responses import APIResponse
from backend.app.schemas.dtos import ParsedDocumentDTO
from backend.app.services.storage import StorageService
from backend.app.services.parser import ParserService
from backend.app.utils.file_helpers import validate_file_size, generate_unique_filename

router = APIRouter()


# -----------------------------
# Helper: list documents by company
# (local helper so you don't need to change crud.py)
# -----------------------------
def list_documents_by_company(session: Session, company_id: int) -> List[Document]:
    """
    Return all Document rows for a given company_id ordered by uploaded_at desc.
    """
    stmt = select(Document).where(Document.company_id == company_id).order_by(Document.uploaded_at.desc())
    results = session.exec(stmt).all()
    return results


# -----------------------------------------------------
# Upload a document (PDF or image)
# -----------------------------------------------------
@router.post("/upload")
async def upload_document(
    company_id: int = Form(...),
    doc_type: str = Form(...),          # "PO" | "INVOICE" | "DELIVERY"
    file: UploadFile = File(...),
    session: Session = Depends(get_session)
):
    """
    Upload a document file (PDF/image), save to storage, create DB record and return document id & path.
    """
    # Validate type
    if doc_type not in ["PO", "INVOICE", "DELIVERY"]:
        raise HTTPException(status_code=400, detail="Invalid document type")

    # Read file bytes
    try:
        file_bytes = await file.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read uploaded file: {e}")

    # Validate size
    try:
        validate_file_size(file_bytes)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"File validation error: {e}")

    # Generate safe filename
    unique_filename = generate_unique_filename(file.filename)

    # Save file (local or S3) via StorageService
    storage = StorageService()
    try:
        saved_path = storage.save(file_bytes, unique_filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")

    # Create DB entry
    try:
        doc = crud.create_document(
            session=session,
            company_id=company_id,
            filename=saved_path,
            doc_type=doc_type
        )
    except Exception as e:
        # If DB create fails, attempt to remove saved file (best-effort)
        try:
            storage.delete(saved_path)
        except Exception:
            pass
        raise HTTPException(status_code=500, detail=f"Failed to create document record: {e}")

    return APIResponse(
        success=True,
        message="File uploaded successfully",
        data={"document_id": doc.id, "path": saved_path}
    )


# -----------------------------------------------------
# Get a document by ID
# -----------------------------------------------------
@router.get("/documents/{doc_id}")
def get_document(doc_id: int, session: Session = Depends(get_session)):
    """
    Retrieve a single document record and return metadata + OCR/parsed JSON (if available).
    """
    doc = crud.get_document(session, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    parsed = None
    if doc.parsed_json:
        try:
            parsed = json.loads(doc.parsed_json)
        except Exception:
            parsed = doc.parsed_json

    return APIResponse(
        success=True,
        data={
            "id": doc.id,
            "company_id": doc.company_id,
            "filename": doc.filename,
            "doc_type": doc.doc_type,
            "uploaded_at": doc.uploaded_at,
            "ocr_text": doc.ocr_text,
            "parsed_json": parsed
        }
    )


# -----------------------------------------------------
# Run OCR only (optional)
# -----------------------------------------------------
@router.post("/documents/{doc_id}/ocr")
def run_ocr(doc_id: int, session: Session = Depends(get_session)):
    """
    Run OCR on an existing saved document and save OCR text into DB.
    """
    doc = crud.get_document(session, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    parser = ParserService()

    try:
        ocr_text = parser.ocr.extract_text(doc.filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR extraction failed: {e}")

    try:
        crud.update_document_ocr(session, doc_id, ocr_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update OCR in DB: {e}")

    return APIResponse(
        success=True,
        message="OCR completed",
        data={"ocr_text": ocr_text}
    )


# -----------------------------------------------------
# Full parse pipeline → OCR + LLM
# -----------------------------------------------------
@router.post("/documents/{doc_id}/parse")
def parse_document(doc_id: int, session: Session = Depends(get_session)):
    """
    Run the full parsing pipeline: OCR + LLM/structure extraction.
    Saves OCR and parsed JSON into DB when available and returns parsed DTO.
    """
    doc = crud.get_document(session, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    parser = ParserService()

    try:
        result = parser.process_document(doc.filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Parsing failed: {e}")

    # Store results in DB
    try:
        if "ocr_text" in result and result["ocr_text"] is not None:
            crud.update_document_ocr(session, doc_id, result["ocr_text"])
        if "parsed" in result and result["parsed"] is not None:
            crud.update_document_parsed(session, doc_id, result["parsed"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save parse result: {e}")

    parsed_payload = None
    if result.get("parsed") is not None:
        parsed_payload = result["parsed"]

    return APIResponse(
        success=True,
        message="Document parsed successfully",
        data=ParsedDocumentDTO(
            ocr_text=result.get("ocr_text"),
            parsed=parsed_payload
        ).dict()
    )


# -----------------------------------------------------
# List documents by company (required query param: company_id)
# -----------------------------------------------------
@router.get("/documents")
def list_documents(company_id: Optional[int] = Query(None, description="Company ID to filter documents"), session: Session = Depends(get_session)):
    """
    List documents. Requires company_id query parameter.
    Returns documents for that company ordered by uploaded_at descending.
    """
    if company_id is None:
        raise HTTPException(status_code=400, detail="company_id query parameter is required")

    try:
        docs = list_documents_by_company(session, company_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to query documents: {e}")

    docs_out = []
    for d in docs:
        parsed = None
        if d.parsed_json:
            try:
                parsed = json.loads(d.parsed_json)
            except Exception:
                parsed = d.parsed_json

        docs_out.append({
            "id": d.id,
            "company_id": d.company_id,
            "filename": d.filename,
            "doc_type": d.doc_type,
            "uploaded_at": d.uploaded_at,
            "ocr_text": d.ocr_text,
            "parsed_json": parsed
        })

    return APIResponse(success=True, data={"documents": docs_out})
