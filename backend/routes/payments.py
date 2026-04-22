from fastapi import APIRouter, Depends, HTTPException, Response
from sqlmodel import Session
from database import get_session
from models import Payment, Client
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/payments", tags=["payments"])

class PaymentCreate(BaseModel):
    client_id: int
    label: str
    value: str

class PaymentPatch(BaseModel):
    label: Optional[str] = None
    value: Optional[str] = None

def _get_or_404(session: Session, payment_id: int) -> Payment:
    p = session.get(Payment, payment_id)
    if not p:
        raise HTTPException(status_code=404, detail="Payment not found")
    return p

@router.post("", status_code=201)
def create_payment(body: PaymentCreate, session: Session = Depends(get_session)):
    if not session.get(Client, body.client_id):
        raise HTTPException(status_code=404, detail="Client not found")
    p = Payment(client_id=body.client_id, label=body.label, value=body.value)
    session.add(p); session.commit(); session.refresh(p)
    return {"id": p.id, "client_id": p.client_id, "label": p.label, "value": p.value}

@router.patch("/{payment_id}")
def patch_payment(payment_id: int, body: PaymentPatch, session: Session = Depends(get_session)):
    p = _get_or_404(session, payment_id)
    for field, val in body.model_dump(exclude_unset=True).items():
        setattr(p, field, val)
    session.add(p); session.commit(); session.refresh(p)
    return {"id": p.id, "client_id": p.client_id, "label": p.label, "value": p.value}

@router.delete("/{payment_id}", status_code=204)
def delete_payment(payment_id: int, session: Session = Depends(get_session)):
    p = _get_or_404(session, payment_id)
    session.delete(p); session.commit()
    return Response(status_code=204)
