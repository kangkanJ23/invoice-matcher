from sqlmodel import Session, select
from backend.app.db.models import Company, Document, Match
from typing import Optional, List
import json
from sqlmodel import select

# ---------------------------------------
# Company CRUD
# ---------------------------------------
def create_company(session: Session, name: str, contact_person: str = None, email: str = None) -> Company:
    company = Company(name=name, contact_person=contact_person, email=email)
    session.add(company)
    session.commit()
    session.refresh(company)
    return company


def get_company(session: Session, company_id: int) -> Optional[Company]:
    return session.get(Company, company_id)


# ---------------------------------------
# Document CRUD
# ---------------------------------------
def create_document(session: Session, company_id: int, filename: str, doc_type: str) -> Document:
    doc = Document(
        company_id=company_id,
        filename=filename,
        doc_type=doc_type
    )
    session.add(doc)
    session.commit()
    session.refresh(doc)
    return doc


def get_document(session: Session, doc_id: int) -> Optional[Document]:
    return session.get(Document, doc_id)


def update_document_ocr(session: Session, doc_id: int, ocr_text: str):
    doc = session.get(Document, doc_id)
    if doc:
        doc.ocr_text = ocr_text
        session.add(doc)
        session.commit()
    return doc


def update_document_parsed(session: Session, doc_id: int, parsed_json: dict):
    doc = session.get(Document, doc_id)
    if doc:
        doc.parsed_json = json.dumps(parsed_json, indent=2)
        session.add(doc)
        session.commit()
    return doc


# ---------------------------------------
# Match CRUD
# ---------------------------------------
def create_match(
    session: Session,
    company_id: int,
    po_id: int,
    invoice_id: int,
    status: str,
    mismatches: dict,
    fraud_flags: list,
    confidence_score: float
) -> Match:

    match_record = Match(
        company_id=company_id,
        po_id=po_id,
        invoice_id=invoice_id,
        status=status,
        mismatches=json.dumps(mismatches, indent=2),
        fraud_flags=json.dumps(fraud_flags, indent=2),
        confidence_score=confidence_score
    )

    session.add(match_record)
    session.commit()
    session.refresh(match_record)
    return match_record


def get_match(session: Session, match_id: int) -> Optional[Match]:
    return session.get(Match, match_id)



def list_documents_by_company(session: Session, company_id: int):
    statement = select(Document).where(Document.company_id == company_id).order_by(Document.uploaded_at.desc())
    results = session.exec(statement).all()
    return results
