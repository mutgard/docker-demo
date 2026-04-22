# Payment CRUD Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Allow Julia to add, edit, and delete individual payment records from the client profile without recreating the entire client.

**Architecture:** New `POST /payments`, `PATCH /payments/{id}`, `DELETE /payments/{id}` routes in a dedicated `payments` router. Frontend adds an inline "add payment" row and edit/delete controls on each existing payment row in ProfileScreen. No new screens needed — the existing payment section in `ProfileScreen.tsx` becomes interactive.

**Tech Stack:** FastAPI + SQLModel `Payment` model (already exists), React inline styles, `T` token system.

---

## File Map

**Backend — new:**
- `backend/routes/payments.py`
- `backend/tests/test_payments.py`

**Backend — modified:**
- `backend/main.py` — register `payments_router`

**Frontend — modified:**
- `frontend/src/types.ts` — add `PaymentCreate`, `PaymentPatch`
- `frontend/src/api.ts` — add `createPayment`, `updatePayment`, `deletePayment`
- `frontend/src/screens/ProfileScreen.tsx` — interactive payment rows + add form

---

## Task 1: Backend payments route + tests

**Files:**
- Create: `backend/routes/payments.py`
- Create: `backend/tests/test_payments.py`
- Modify: `backend/main.py`

- [ ] **Step 1.1: Write the failing tests**

Create `backend/tests/test_payments.py`:

```python
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
    # verify it's gone by checking client
    r3 = client.get(f"/clients/{cid}")
    assert all(p["id"] != pid for p in r3.json()["payments"])

def test_patch_payment_not_found(client):
    r = client.patch("/payments/9999", json={"label": "X"})
    assert r.status_code == 404
```

- [ ] **Step 1.2: Run tests to verify they fail**

```bash
cd backend && python -m pytest tests/test_payments.py -v
```

Expected: FAIL (routes don't exist yet)

- [ ] **Step 1.3: Create backend/routes/payments.py**

```python
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlmodel import Session
from database import get_session
from models import Payment, Client
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/payments", tags=["payments"])

class PaymentCreate(BaseModel):
    client_id: int
    label: str
    value: str

class PaymentPatch(BaseModel):
    label: Optional[str] = None
    value: Optional[str] = None

def _get_or_404(session: Session, payment_id: int) -> Payment:
    p = session.get(Payment, payment_id)
    if not p:
        raise HTTPException(status_code=404, detail="Payment not found")
    return p

@router.post("", status_code=201)
def create_payment(body: PaymentCreate, session: Session = Depends(get_session)):
    if not session.get(Client, body.client_id):
        raise HTTPException(status_code=404, detail="Client not found")
    p = Payment(client_id=body.client_id, label=body.label, value=body.value)
    session.add(p); session.commit(); session.refresh(p)
    return {"id": p.id, "client_id": p.client_id, "label": p.label, "value": p.value}

@router.patch("/{payment_id}")
def patch_payment(payment_id: int, body: PaymentPatch, session: Session = Depends(get_session)):
    p = _get_or_404(session, payment_id)
    for field, val in body.model_dump(exclude_unset=True).items():
        setattr(p, field, val)
    session.add(p); session.commit(); session.refresh(p)
    return {"id": p.id, "client_id": p.client_id, "label": p.label, "value": p.value}

@router.delete("/{payment_id}", status_code=204)
def delete_payment(payment_id: int, session: Session = Depends(get_session)):
    p = _get_or_404(session, payment_id)
    session.delete(p); session.commit()
    return Response(status_code=204)
```

- [ ] **Step 1.4: Register in main.py**

Add after the existing imports:
```python
from routes.payments import router as payments_router
```

Add after `app.include_router(events_router)`:
```python
app.include_router(payments_router)
```

- [ ] **Step 1.5: Run tests to verify they pass**

```bash
cd backend && python -m pytest tests/test_payments.py -v
```

Expected: all 5 tests PASS

- [ ] **Step 1.6: Commit**

```bash
git add backend/routes/payments.py backend/tests/test_payments.py backend/main.py
git commit -m "feat(backend): payment CRUD routes — POST/PATCH/DELETE"
```

---

## Task 2: Frontend types and API methods

**Files:**
- Modify: `frontend/src/types.ts`
- Modify: `frontend/src/api.ts`

- [ ] **Step 2.1: Add PaymentCreate to types.ts**

Append to `frontend/src/types.ts`:

```typescript
export interface PaymentCreate {
  client_id: number;
  label: string;
  value: string;
}
```

- [ ] **Step 2.2: Add payment API methods to api.ts**

Update the import line to include `PaymentCreate`:
```typescript
import type {
  Client, Fabric, ShoppingItem, IntakeData, ClientBrief, ClientCreate,
  AtelierEvent, AppointmentCreate, DeliveryCreate, PaymentCreate,
} from './types';
```

Add to the `api` object after `patchFabric`:
```typescript
  createPayment: (body: PaymentCreate) =>
    post<{ id: number; client_id: number; label: string; value: string }>('/payments', body),
  updatePayment: (id: number, body: { label?: string; value?: string }) =>
    patch<{ id: number; client_id: number; label: string; value: string }>(`/payments/${id}`, body),
  deletePayment: (id: number) =>
    del(`/payments/${id}`),
```

- [ ] **Step 2.3: Commit**

```bash
git add frontend/src/types.ts frontend/src/api.ts
git commit -m "feat(types+api): PaymentCreate type + createPayment/updatePayment/deletePayment"
```

---

## Task 3: Interactive payment rows in ProfileScreen

**Files:**
- Modify: `frontend/src/screens/ProfileScreen.tsx`

- [ ] **Step 3.1: Add payment editing state**

After the existing `const [clientEvents, setClientEvents]` state line, add:

```tsx
const [editingPaymentId, setEditingPaymentId] = useState<number | null>(null);
const [paymentDraft, setPaymentDraft] = useState({ label: '', value: '' });
const [addingPayment, setAddingPayment] = useState(false);
const [newPayment, setNewPayment] = useState({ label: '', value: '' });
```

- [ ] **Step 3.2: Add payment action handlers**

After `saveEdit`, add:

```tsx
const startEditPayment = (p: { id: number; label: string; value: string }) => {
  setEditingPaymentId(p.id);
  setPaymentDraft({ label: p.label, value: p.value });
};

const savePayment = async (id: number) => {
  await api.updatePayment(id, paymentDraft);
  const updated = await api.getClient(c.id);
  setC(updated);
  setEditingPaymentId(null);
};

const deletePayment = async (id: number) => {
  await api.deletePayment(id);
  const updated = await api.getClient(c.id);
  setC(updated);
};

const addPayment = async () => {
  if (!newPayment.label.trim() || !newPayment.value.trim()) return;
  await api.createPayment({ client_id: c.id, label: newPayment.label, value: newPayment.value });
  const updated = await api.getClient(c.id);
  setC(updated);
  setAddingPayment(false);
  setNewPayment({ label: '', value: '' });
};
```

- [ ] **Step 3.3: Replace the payment rows rendering**

In the `{/* Payment progress */}` section, replace the `{c.payments.map(...)}` block with:

```tsx
<div style={{ marginTop: 8 }}>
  {c.payments.map((p, i) => (
    <div key={p.id} style={{ borderBottom: i < c.payments.length - 1 ? `1px solid ${T.hairline}` : 'none' }}>
      {editingPaymentId === p.id ? (
        <div style={{ display: 'flex', gap: 8, padding: '6px 0', alignItems: 'center' }}>
          <input
            value={paymentDraft.label}
            onChange={e => setPaymentDraft(d => ({ ...d, label: e.target.value }))}
            style={{ flex: 1, border: 'none', borderBottom: `1px solid ${T.hairline2}`, background: 'transparent', outline: 'none', fontFamily: T.mono, fontSize: 10, color: T.ink }}
          />
          <input
            value={paymentDraft.value}
            onChange={e => setPaymentDraft(d => ({ ...d, value: e.target.value }))}
            style={{ flex: 1, border: 'none', borderBottom: `1px solid ${T.hairline2}`, background: 'transparent', outline: 'none', fontFamily: T.mono, fontSize: 10, color: T.ink, textAlign: 'right' }}
          />
          <button onClick={() => savePayment(p.id)} style={{ background: 'none', border: 'none', cursor: 'pointer', fontFamily: T.mono, fontSize: 9, color: T.accent, padding: 0, letterSpacing: 0.6 }}>✓</button>
          <button onClick={() => setEditingPaymentId(null)} style={{ background: 'none', border: 'none', cursor: 'pointer', fontFamily: T.mono, fontSize: 9, color: T.ink3, padding: 0, letterSpacing: 0.6 }}>✕</button>
        </div>
      ) : (
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '5px 0' }}>
          <Mono size={10} color={T.ink3}>{p.label}</Mono>
          <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
            <Mono size={10} color={T.ink}>{p.value}</Mono>
            <button onClick={() => startEditPayment(p)} style={{ background: 'none', border: 'none', cursor: 'pointer', fontFamily: T.mono, fontSize: 9, color: T.ink3, padding: 0, opacity: 0.6 }}>Editar</button>
            <button onClick={() => deletePayment(p.id)} style={{ background: 'none', border: 'none', cursor: 'pointer', fontFamily: T.mono, fontSize: 9, color: T.accent, padding: 0, opacity: 0.7 }}>✕</button>
          </div>
        </div>
      )}
    </div>
  ))}

  {/* Add payment row */}
  {addingPayment ? (
    <div style={{ display: 'flex', gap: 8, padding: '8px 0', alignItems: 'center', borderTop: `1px solid ${T.hairline}`, marginTop: 4 }}>
      <input
        value={newPayment.label}
        onChange={e => setNewPayment(d => ({ ...d, label: e.target.value }))}
        placeholder="Concepte"
        style={{ flex: 1, border: 'none', borderBottom: `1px solid ${T.hairline2}`, background: 'transparent', outline: 'none', fontFamily: T.mono, fontSize: 10, color: T.ink, padding: '2px 0' }}
      />
      <input
        value={newPayment.value}
        onChange={e => setNewPayment(d => ({ ...d, value: e.target.value }))}
        placeholder="€500 rebut"
        style={{ flex: 1, border: 'none', borderBottom: `1px solid ${T.hairline2}`, background: 'transparent', outline: 'none', fontFamily: T.mono, fontSize: 10, color: T.ink, textAlign: 'right', padding: '2px 0' }}
      />
      <button onClick={addPayment} style={{ background: 'none', border: 'none', cursor: 'pointer', fontFamily: T.mono, fontSize: 9, color: T.accent, padding: 0, letterSpacing: 0.6 }}>+ Afegir</button>
      <button onClick={() => { setAddingPayment(false); setNewPayment({ label: '', value: '' }); }} style={{ background: 'none', border: 'none', cursor: 'pointer', fontFamily: T.mono, fontSize: 9, color: T.ink3, padding: 0 }}>✕</button>
    </div>
  ) : (
    <button
      onClick={() => setAddingPayment(true)}
      style={{ marginTop: 8, background: 'none', border: 'none', cursor: 'pointer', fontFamily: T.mono, fontSize: 9, letterSpacing: 0.8, textTransform: 'uppercase', color: T.ink3, padding: 0, display: 'block' }}
    >
      + Pagament
    </button>
  )}
</div>
```

Also update the `{/* Payment progress */}` outer condition from `{priceTotal !== null && (...)}` to:
```tsx
{(priceTotal !== null || c.payments.length === 0) && (
```

So the section always renders (even with no payments) so Julia can add the first one.

- [ ] **Step 3.4: Verify manually**

```bash
cd frontend && npm run dev
```

1. Open any client profile with existing payments
2. Click "Editar" on a payment row → inline edit fields appear
3. Change value, click ✓ → updated immediately
4. Click ✕ on a payment → confirm it's removed
5. Click "+ Pagament" → new row form appears
6. Fill in "Senyal" / "€500 rebut" → click "+ Afegir" → row appears, progress bar updates

- [ ] **Step 3.5: Commit**

```bash
git add frontend/src/screens/ProfileScreen.tsx
git commit -m "feat(profile): interactive payment rows — add/edit/delete inline"
```

---

## Self-Review

**Spec coverage:**
- `POST /payments` ✓
- `PATCH /payments/{id}` ✓
- `DELETE /payments/{id}` ✓
- Frontend: add payment row ✓
- Frontend: edit payment inline ✓
- Frontend: delete payment ✓
- Payment progress bar updates after change ✓ (re-fetches client)

**Type consistency:** `PaymentCreate.client_id` is `number`, matches `Payment.client_id` in the model. `api.createPayment` returns `{ id, client_id, label, value }` which matches what the backend serializes. `paymentDraft` is `{ label: string; value: string }` matching `PaymentPatch`.
