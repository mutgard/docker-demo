from fastapi import APIRouter, HTTPException
import json
import os

router = APIRouter(prefix="/clients", tags=["intake"])

@router.get("/{client_id}/intake")
def get_intake(client_id: int):
    base = os.path.dirname(os.path.abspath(__file__))
    path = os.path.normpath(os.path.join(base, f"../data/intake/client_{client_id}.json"))
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="No intake data for this client")
    with open(path, encoding="utf-8") as f:
        return json.load(f)
