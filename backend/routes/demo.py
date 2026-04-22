from fastapi import APIRouter, HTTPException
import json
import os

router = APIRouter(prefix="/demo-scenarios", tags=["demo"])

SCENARIOS_DIR = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "../data/demo-scenarios")
)

def _load(scenario_id: str) -> dict:
    safe_dir = os.path.abspath(SCENARIOS_DIR)
    path = os.path.abspath(os.path.join(safe_dir, f"{scenario_id}.json"))
    if not path.startswith(safe_dir + os.sep):
        raise HTTPException(status_code=404, detail="Scenario not found")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Scenario not found")
    with open(path, encoding="utf-8") as f:
        return json.load(f)

@router.get("")
def list_scenarios():
    if not os.path.isdir(SCENARIOS_DIR):
        return []
    result = []
    for fname in sorted(os.listdir(SCENARIOS_DIR)):
        if fname.endswith(".json"):
            data = _load(fname[:-5])
            result.append({"id": data["id"], "label": data["label"]})
    return result

@router.get("/{scenario_id}")
def get_scenario(scenario_id: str):
    return _load(scenario_id)
