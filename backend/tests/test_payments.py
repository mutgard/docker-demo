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

def _make_client(client):
    r = client.post("/clients", json={
        "name": "Test", "wedding_date": "01 Jun 2026", "days_until": 43,
        "status": "clienta", "garment": "", "phone": "", "email": "",
        "garment_style": "", "measurements_date": "", "notes": "",
        "appointments": [], "payments": [], "fabrics": []
    })
    return r.json()["id"]

def test_create_payment(client):
    cid = _make_client(client)
    r = client.post("/payments", json={"client_id": cid, "label": "Senyal", "value": "€500 rebut"})
    assert r.status_code == 201
    data = r.json()
    assert data["id"] is not None
    assert data["label"] == "Senyal"
    assert data["value"] == "€500 rebut"
    assert data["client_id"] == cid

def test_create_payment_bad_client(client):
    r = client.post("/payments", json={"client_id": 9999, "label": "X", "value": "Y"})
    assert r.status_code == 404

def test_patch_payment(client):
    cid = _make_client(client)
    r = client.post("/payments", json={"client_id": cid, "label": "Senyal", "value": "€500 rebut"})
    pid = r.json()["id"]
    r2 = client.patch(f"/payments/{pid}", json={"value": "€600 rebut"})
    assert r2.status_code == 200
    assert r2.json()["value"] == "€600 rebut"

def test_delete_payment(client):
    cid = _make_client(client)
    r = client.post("/payments", json={"client_id": cid, "label": "Senyal", "value": "€500 rebut"})
    pid = r.json()["id"]
    r2 = client.delete(f"/payments/{pid}")
    assert r2.status_code == 204
    r3 = client.get(f"/clients/{cid}")
    assert all(p["id"] != pid for p in r3.json()["payments"])

def test_patch_payment_not_found(client):
    r = client.patch("/payments/9999", json={"label": "X"})
    assert r.status_code == 404
