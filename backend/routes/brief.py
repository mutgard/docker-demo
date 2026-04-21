from fastapi import APIRouter, HTTPException
import json
import os
import glob

router = APIRouter(prefix="/api/brief", tags=["brief"])

@router.get("/{token}")
def get_brief(token: str):
    base = os.path.dirname(os.path.abspath(__file__))
    intake_dir = os.path.normpath(os.path.join(base, "../data/intake"))
    for path in sorted(glob.glob(os.path.join(intake_dir, "client_*.json"))):
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        if data.get("token") == token:
            brief = data.get("brief", {})
            return {
                "client_name": data.get("client_name", ""),
                "wedding_date": brief.get("wedding_date", ""),
                "venue": brief.get("venue", ""),
                "garment": brief.get("garment", ""),
                "style": brief.get("style", ""),
                "fabric_notes": brief.get("fabric_notes", ""),
            }
    raise HTTPException(status_code=404, detail="Brief not found")
