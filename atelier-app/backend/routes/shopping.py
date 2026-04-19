from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from database import get_session
from models import Fabric, Client

router = APIRouter(prefix="/shopping", tags=["shopping"])

@router.get("")
def get_shopping_list(session: Session = Depends(get_session)):
    fabrics = session.exec(select(Fabric).where(Fabric.to_buy == True)).all()
    result = []
    for f in fabrics:
        c = session.get(Client, f.client_id)
        result.append({
            "id": f.id, "name": f.name, "use": f.use, "qty": f.qty,
            "price": f.price, "to_buy": f.to_buy, "supplier": f.supplier,
            "client_id": f.client_id,
            "client_name": c.name if c else "",
        })
    return result
