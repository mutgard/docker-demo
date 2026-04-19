from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import Optional
from database import get_session
from models import Fabric
from pydantic import BaseModel

router = APIRouter(prefix="/fabrics", tags=["fabrics"])

class FabricPatch(BaseModel):
    name: Optional[str] = None
    use: Optional[str] = None
    qty: Optional[str] = None
    price: Optional[str] = None
    to_buy: Optional[bool] = None
    supplier: Optional[str] = None

@router.get("")
def list_fabrics(client_id: Optional[int] = None,
                 session: Session = Depends(get_session)):
    q = select(Fabric)
    if client_id is not None:
        q = q.where(Fabric.client_id == client_id)
    return session.exec(q).all()

@router.patch("/{fabric_id}")
def patch_fabric(fabric_id: int, body: FabricPatch,
                 session: Session = Depends(get_session)):
    f = session.get(Fabric, fabric_id)
    if not f:
        raise HTTPException(status_code=404, detail="Fabric not found")
    for field, val in body.model_dump(exclude_unset=True).items():
        setattr(f, field, val)
    session.add(f); session.commit(); session.refresh(f)
    return f
