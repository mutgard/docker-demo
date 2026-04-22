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

def test_create_delivery(client):
    r = client.post("/deliveries", json={
        "supplier": "Gratacós", "description": "Mikado seda 3m",
        "expected_date": "2026-04-25", "client_id": None, "received": False
    })
    assert r.status_code == 201
    d = r.json()
    assert d["type"] == "delivery"
    assert d["supplier"] == "Gratacós"
    assert d["date"] == "2026-04-25"
    assert d["title"] == "Mikado seda 3m"
    assert d["received"] is False

def test_update_delivery(client):
    did = client.post("/deliveries", json={
        "supplier": "Gratacós", "description": "Mikado 3m",
        "expected_date": "2026-04-25", "client_id": None, "received": False
    }).json()["id"]
    r = client.patch(f"/deliveries/{did}", json={"received": True, "expected_date": "2026-04-28"})
    assert r.status_code == 200
    assert r.json()["received"] is True
    assert r.json()["date"] == "2026-04-28"

def test_delete_delivery(client):
    did = client.post("/deliveries", json={
        "supplier": "Ribes", "description": "Tul", "expected_date": "2026-05-01",
        "client_id": None, "received": False
    }).json()["id"]
    assert client.delete(f"/deliveries/{did}").status_code == 204
    assert client.get(f"/deliveries/{did}").status_code == 404

def test_delivery_linked_to_client(client):
    cid = client.post("/clients", json={
        "name": "Test", "wedding_date": "01 Jun 2026", "days_until": 40,
        "status": "clienta", "garment": "", "phone": "", "email": "",
        "garment_style": "", "measurements_date": "", "notes": "",
        "appointments": [], "payments": [], "fabrics": []
    }).json()["id"]
    r = client.post("/deliveries", json={
        "supplier": "Gratacós", "description": "Seda",
        "expected_date": "2026-05-01", "client_id": cid, "received": False
    })
    assert r.status_code == 201
    assert r.json()["client_id"] == cid
    assert r.json()["client_name"] == "Test"

def test_delivery_404(client):
    assert client.patch("/deliveries/9999", json={"received": True}).status_code == 404
    assert client.delete("/deliveries/9999").status_code == 404
