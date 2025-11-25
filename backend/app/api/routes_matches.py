from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from backend.app.db.session import get_session
from backend.app.db import crud
from backend.app.schemas.dtos import MatchRequestDTO, MatchResultDTO
from backend.app.schemas.responses import APIResponse
from backend.app.services.matcher import MatcherService
from backend.app.services.report import ReportService
import json

router = APIRouter()


# -----------------------------------------------------
# Perform PO–Invoice matching
# -----------------------------------------------------
@router.post("/match")
def match_documents(payload: MatchRequestDTO, session: Session = Depends(get_session)):
    # Fetch PO
    po_doc = crud.get_document(session, payload.po_id)
    if not po_doc:
        raise HTTPException(status_code=404, detail="PO document not found")

    # Fetch Invoice
    inv_doc = crud.get_document(session, payload.invoice_id)
    if not inv_doc:
        raise HTTPException(status_code=404, detail="Invoice document not found")

    # Parsed JSON must exist
    if not po_doc.parsed_json or not inv_doc.parsed_json:
        raise HTTPException(status_code=400, detail="Both documents must be parsed first")

    po = json.loads(po_doc.parsed_json)
    inv = json.loads(inv_doc.parsed_json)

    matcher = MatcherService()
    result = matcher.match_po_and_invoice(po, inv)

    # Save match result in DB
    match_record = crud.create_match(
        session=session,
        company_id=payload.company_id,
        po_id=payload.po_id,
        invoice_id=payload.invoice_id,
        status="Matched" if not result["mismatches"] and not result["fraud_flags"]
               else ("Warning" if result["score"] >= 60 else "Failed"),
        mismatches=result["mismatches"],
        fraud_flags=result["fraud_flags"],
        confidence_score=result["score"]
    )

    # Generate PDF report
    report_service = ReportService()
    report_path = report_service.generate_match_report(
        match_id=match_record.id,
        po=po,
        inv=inv,
        result=result
    )

    # Return response
    return APIResponse(
        success=True,
        message="Match completed",
        data={
            "match_id": match_record.id,
            "result": MatchResultDTO(
                mismatches=result["mismatches"],
                fraud_flags=result["fraud_flags"],
                score=result["score"]
            ).dict(),
            "report_path": report_path
        }
    )


# -----------------------------------------------------
# Retrieve match result by ID
# -----------------------------------------------------
@router.get("/match/{match_id}")
def get_match(match_id: int, session: Session = Depends(get_session)):
    match_record = crud.get_match(session, match_id)
    if not match_record:
        raise HTTPException(status_code=404, detail="Match result not found")

    return APIResponse(
        success=True,
        data={
            "id": match_record.id,
            "company_id": match_record.company_id,
            "po_id": match_record.po_id,
            "invoice_id": match_record.invoice_id,
            "status": match_record.status,
            "mismatches": match_record.mismatches,
            "fraud_flags": match_record.fraud_flags,
            "confidence_score": match_record.confidence_score,
            "created_at": match_record.created_at
        }
    )
