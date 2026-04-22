from fastapi import APIRouter, Depends, HTTPException, Response
from sqlmodel import Session
from database import get_session
from models import Delivery, Client
from schemas import DeliveryCreate, DeliveryPatch

router = APIRouter(prefix="/deliveries", tags=["deliveries"])

def _get_or_404(session: Session, del_id: int) -> Delivery:
    d = session.get(Delivery, del_id)
    if not d:
        raise HTTPException(status_code=404, detail="Delivery not found")
    return d

def _to_event(d: Delivery, session: Session) -> dict:
    c = session.get(Client, d.client_id) if d.client_id else None
    return {
        "id": d.id, "type": "delivery",
        "date": d.expected_date, "title": d.description,
        "client_id": d.client_id,
        "client_name": c.name if c else None,
        "order_id": None, "supplier": d.supplier, "received": d.received,
    }

@router.get("/{del_id}")
def get_delivery(del_id: int, session: Session = Depends(get_session)):
    return _to_event(_get_or_404(session, del_id), session)

@router.post("", status_code=201)
def create_delivery(body: DeliveryCreate, session: Session = Depends(get_session)):
    d = Delivery(
        client_id=body.client_id, supplier=body.supplier,
        description=body.description, expected_date=body.expected_date,
        received=body.received,
    )
    session.add(d); session.commit(); session.refresh(d)
    return _to_event(d, session)

@router.patch("/{del_id}")
def update_delivery(del_id: int, body: DeliveryPatch,
                    session: Session = Depends(get_session)):
    d = _get_or_404(session, del_id)
    for field, val in body.model_dump(exclude_unset=True).items():
        setattr(d, field, val)
    session.add(d); session.commit(); session.refresh(d)
    return _to_event(d, session)

@router.delete("/{del_id}", status_code=204)
def delete_delivery(del_id: int, session: Session = Depends(get_session)):
    d = _get_or_404(session, del_id)
    session.delete(d); session.commit()
    return Response(status_code=204)
