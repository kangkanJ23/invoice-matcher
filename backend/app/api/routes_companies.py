from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from backend.app.db.session import get_session
from backend.app.db import crud
from backend.app.db.models import Company
from backend.app.schemas.responses import APIResponse

router = APIRouter()


@router.post("/companies", tags=["Companies"])
def create_company(name: str, contact_person: str = None, email: str = None, session: Session = Depends(get_session)):
    """
    Create a company.
    Form params (use Swagger UI or query params):
     - name (required)
     - contact_person (optional)
     - email (optional)
    Returns created company id.
    """
    if not name:
        raise HTTPException(status_code=400, detail="Company name is required")

    company = crud.create_company(session=session, name=name, contact_person=contact_person, email=email)
    return APIResponse(success=True, message="Company created", data={"company_id": company.id}).dict()


@router.get("/companies", tags=["Companies"])
def list_companies(session: Session = Depends(get_session)):
    """
    List companies (basic).
    """
    statement = select(crud.Company) if False else None  # placeholder - we will use crud only
    # simple direct query using SQLModel Session
    results = session.exec(select(crud.Company)).all()
    companies = [{"id": c.id, "name": c.name, "contact_person": c.contact_person, "email": c.email} for c in results]
    return APIResponse(success=True, data={"companies": companies}).dict()
