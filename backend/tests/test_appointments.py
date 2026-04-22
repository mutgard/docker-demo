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
        "name": "Test", "wedding_date": "01 Jun 2026", "days_until": 40,
        "status": "clienta", "garment": "", "phone": "", "email": "",
        "garment_style": "", "measurements_date": "", "notes": "",
        "appointments": [], "payments": [], "fabrics": []
    })
    return r.json()["id"]

def test_create_appointment(client):
    cid = _make_client(client)
    r = client.post("/appointments", json={
        "client_id": cid, "title": "Primera prova", "date": "2026-04-15", "order_id": None
    })
    assert r.status_code == 201
    ev = r.json()
    assert ev["type"] == "appointment"
    assert ev["date"] == "2026-04-15"
    assert ev["title"] == "Primera prova"
    assert ev["client_id"] == cid

def test_create_appointment_no_client(client):
    r = client.post("/appointments", json={
        "client_id": None, "title": "Reunió estudi", "date": "2026-04-30", "order_id": None
    })
    assert r.status_code == 201
    assert r.json()["client_id"] is None

def test_update_appointment(client):
    cid = _make_client(client)
    aid = client.post("/appointments", json={
        "client_id": cid, "title": "Primera prova", "date": "2026-04-15", "order_id": None
    }).json()["id"]
    r = client.patch(f"/appointments/{aid}", json={"title": "Prova actualitzada", "date": "2026-04-20"})
    assert r.status_code == 200
    assert r.json()["title"] == "Prova actualitzada"
    assert r.json()["date"] == "2026-04-20"

def test_delete_appointment(client):
    cid = _make_client(client)
    aid = client.post("/appointments", json={
        "client_id": cid, "title": "Prova", "date": "2026-04-15", "order_id": None
    }).json()["id"]
    assert client.delete(f"/appointments/{aid}").status_code == 204
    # Verify deleted: second delete should 404
    assert client.delete(f"/appointments/{aid}").status_code == 404

def test_appointment_404(client):
    assert client.patch("/appointments/9999", json={"title": "x"}).status_code == 404
    assert client.delete("/appointments/9999").status_code == 404
