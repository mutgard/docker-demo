import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from fastapi.testclient import TestClient
from sqlmodel import create_engine, Session, SQLModel
from main import app
from database import get_session

@pytest.fixture(name="client")
def client_fixture(tmp_path):
    url = f"sqlite:///{tmp_path}/test.db"
    eng = create_engine(url)
    SQLModel.metadata.create_all(eng)
    def override():
        with Session(eng) as s:
            yield s
    app.dependency_overrides[get_session] = override
    yield TestClient(app)
    app.dependency_overrides.clear()

def test_list_demo_scenarios_returns_summaries(client):
    r = client.get("/demo-scenarios")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) == 3
    ids = [s["id"] for s in data]
    assert "boho-2026" in ids
    assert "classic-2026" in ids
    assert "destination-2026" in ids
    for s in data:
        assert set(s.keys()) == {"id", "label"}

def test_get_demo_scenario_boho(client):
    r = client.get("/demo-scenarios/boho-2026")
    assert r.status_code == 200
    data = r.json()
    assert data["id"] == "boho-2026"
    assert "thread" in data
    assert "brief" in data
    assert "client_defaults" in data
    assert len(data["thread"]) > 0

def test_get_demo_scenario_not_found(client):
    r = client.get("/demo-scenarios/nonexistent")
    assert r.status_code == 404

def test_path_traversal_rejected(client):
    r = client.get("/demo-scenarios/../../main")
    assert r.status_code == 404
