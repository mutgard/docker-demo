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

@pytest.fixture(name="client_id")
def client_id_fixture(client):
    r = client.post("/clients", json={
        "name": "Aina", "wedding_date": "17 Mai 2026", "days_until": 28,
        "status": "clienta", "garment": "Vestit", "phone": "", "email": "",
        "garment_style": "", "measurements_date": "", "notes": "",
        "appointments": [], "payments": [],
        "fabrics": [{"name": "Mikado seda", "use": "Cos", "qty": "3.2 m",
                     "price": "€48/m", "to_buy": True, "supplier": "Gratacós"}]
    })
    return r.json()["id"]

def test_list_fabrics_by_client(client, client_id):
    r = client.get(f"/fabrics?client_id={client_id}")
    assert r.status_code == 200
    assert len(r.json()) == 1
    assert r.json()[0]["name"] == "Mikado seda"

def test_patch_fabric_to_buy(client, client_id):
    r = client.get(f"/fabrics?client_id={client_id}")
    fid = r.json()[0]["id"]
    r2 = client.patch(f"/fabrics/{fid}", json={"to_buy": False})
    assert r2.status_code == 200
    assert r2.json()["to_buy"] is False

def test_shopping_list_only_to_buy(client, client_id):
    r = client.get("/shopping")
    assert r.status_code == 200
    items = r.json()
    assert all(item["to_buy"] for item in items)
    assert any(item["name"] == "Mikado seda" for item in items)
    # Each shopping item must include client_name
    assert all("client_name" in item for item in items)
