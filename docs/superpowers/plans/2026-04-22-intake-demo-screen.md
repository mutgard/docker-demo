# Intake Demo Screen Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a standalone "Ingrés" screen with a scenario switcher that simulates the full intake flow — WhatsApp thread → brief → client card — with a "Crear clienta" button that writes the record to the database.

**Architecture:** Backend adds a `/demo-scenarios` router that serves static JSON files from `backend/data/demo-scenarios/`. Frontend adds `IntakeDemoScreen` with a scenario dropdown, a 3-column desktop layout (thread / brief / client card + action), and a tab-based mobile layout. The "Crear clienta" button calls the existing `POST /clients` endpoint. WhatsApp bubble rendering and brief display are self-contained inside `IntakeDemoScreen` (no extraction needed — small enough to inline).

**Tech Stack:** FastAPI static JSON serving, React + TypeScript, existing `T` token system, existing `api.createClient`.

---

## File Map

**Backend — new:**
- `backend/data/demo-scenarios/boho-2026.json`
- `backend/data/demo-scenarios/classic-2026.json`
- `backend/data/demo-scenarios/destination-2026.json`
- `backend/routes/demo.py`
- `backend/tests/test_demo.py`

**Backend — modified:**
- `backend/main.py` — register `demo_router`

**Frontend — new:**
- `frontend/src/screens/IntakeDemoScreen.tsx`

**Frontend — modified:**
- `frontend/src/types.ts` — add `DemoScenarioSummary`, `DemoScenario`, `DemoClientDefaults`
- `frontend/src/api.ts` — add `listDemoScenarios`, `getDemoScenario`
- `frontend/src/App.tsx` — add `'intake'` to `Screen` type, render `IntakeDemoScreen`
- `frontend/src/components/Sidebar.tsx` — add `06 Ingrés` nav item
- `frontend/src/components/MobileShell.tsx` — add `Ingrés` tab

---

## Task 1: Demo scenario JSON files

**Files:**
- Create: `backend/data/demo-scenarios/boho-2026.json`
- Create: `backend/data/demo-scenarios/classic-2026.json`
- Create: `backend/data/demo-scenarios/destination-2026.json`

- [ ] **Step 1.1: Create boho-2026.json**

```json
{
  "id": "boho-2026",
  "label": "Novia Boho — Nov 2026",
  "source": "whatsapp",
  "thread": [
    {"role": "client", "text": "Hola! M'han recomanat el teu atelier. Estic buscant vestit de núvia per al novembre.", "time": "14:32"},
    {"role": "julia", "text": "Hola! Quina il·lusió. Tens alguna idea de l'estil que busques?", "time": "14:35"},
    {"role": "client", "text": "Sí! Vull quelcom boho, molt fluido, romàntic. Res estructurat.", "time": "14:37"},
    {"role": "julia", "text": "M'encanta! Cerimònia interior o exterior?", "time": "14:40"},
    {"role": "client", "text": "Exterior, en un mas. Uns 80 convidats.", "time": "14:41"},
    {"role": "julia", "text": "Perfecte per a gasa o crep de seda. Vols mànigues? Escot?", "time": "14:43"},
    {"role": "client", "text": "Mànigues llargues de gasa, escot paraula d'honor. I cola llarga!", "time": "14:45"},
    {"role": "julia", "text": "Una cola catedralícia amb gasa fluïda és magnètica en un mas. Pressupost?", "time": "14:48"},
    {"role": "client", "text": "Tinc uns 2.000€.", "time": "14:49"},
    {"role": "julia", "text": "Podem treballar-ho perfectament. Et proposo quedar per mides i mostres. Quan et va bé?", "time": "14:52"}
  ],
  "brief": {
    "wedding_date": "14 Nov 2026",
    "venue": "Mas rural, cerimònia exterior",
    "garment": "Vestit a mida · Boho fluido",
    "style": "Paraula d'honor, mànigues llargues de gasa, cola catedralícia, romàntic",
    "budget_tier": "Estàndard · 2.000€",
    "fabric_notes": "Gasa ivori (cos i mànigues), seda crep (folre)",
    "extra_notes": "80 convidats. Cerimònia exterior. Res estructurat."
  },
  "client_defaults": {
    "name": "Núria Bosch",
    "wedding_date": "14.11.2026",
    "wedding_date_iso": "2026-11-14",
    "days_until": 206,
    "status": "prospect",
    "garment": "Vestit a mida",
    "garment_style": "Boho fluido",
    "phone": "",
    "email": "",
    "notes": "Boho, gasa, cola catedralícia. Mas rural. 80 convidats. 2.000€"
  }
}
```

- [ ] **Step 1.2: Create classic-2026.json**

```json
{
  "id": "classic-2026",
  "label": "Novia Clàssica — Jun 2026",
  "source": "whatsapp",
  "thread": [
    {"role": "client", "text": "Buenos días, quería información sobre vestidos de novia a medida.", "time": "10:15"},
    {"role": "julia", "text": "¡Buenos días! Cuéntame, ¿tienes algún estilo en mente?", "time": "10:18"},
    {"role": "client", "text": "Quiero algo muy clásico y elegante. Sirena, con encaje.", "time": "10:20"},
    {"role": "julia", "text": "Sirena con encaje es atemporal. ¿Tienes fecha?", "time": "10:22"},
    {"role": "client", "text": "Sí, el 20 de junio. Boda en una iglesia, luego finca.", "time": "10:23"},
    {"role": "julia", "text": "Junio en una finca es precioso. ¿Escote? ¿Mangas?", "time": "10:25"},
    {"role": "client", "text": "Escote en V con encaje, sin mangas. Y cola semilarga.", "time": "10:27"},
    {"role": "julia", "text": "Para sirena con encaje trabajo con Chantilly o guipure. Presupuesto aproximado?", "time": "10:30"},
    {"role": "client", "text": "Tengo entre 3.000 y 3.500€.", "time": "10:31"},
    {"role": "julia", "text": "Perfecto para un encaje de alta calidad. ¿Cuándo podemos quedar?", "time": "10:34"}
  ],
  "brief": {
    "wedding_date": "20 Jun 2026",
    "venue": "Església + finca",
    "garment": "Vestit a mida · Sirena clàssic",
    "style": "Escot en V amb encaix, sense mànigues, cola semillarga, elegant",
    "budget_tier": "Premium · 3.000–3.500€",
    "fabric_notes": "Encaix Chantilly o guipure (cos), crep (falda sirena)",
    "extra_notes": "Cerimònia religiosa. Finca exterior. Estil atemporal."
  },
  "client_defaults": {
    "name": "Carmen Iglesias",
    "wedding_date": "20.06.2026",
    "wedding_date_iso": "2026-06-20",
    "days_until": 59,
    "status": "prospect",
    "garment": "Vestit a mida",
    "garment_style": "Sirena clàssic",
    "phone": "",
    "email": "",
    "notes": "Sirena, encaix Chantilly, escot en V. Finca. 3.000–3.500€"
  }
}
```

- [ ] **Step 1.3: Create destination-2026.json**

```json
{
  "id": "destination-2026",
  "label": "Destination Wedding — Sep 2026",
  "source": "web_form",
  "submitted_at": "2026-04-10T09:22:00",
  "form_data": {
    "name": "Sophie Laurent",
    "email": "sophie.laurent@mail.fr",
    "phone": "+33 6 12 34 56 78",
    "wedding_date": "12 septembre 2026",
    "venue": "Costa Brava, platja exterior",
    "style_notes": "Minimalista, columna, línies netes. Res de vol ni encaix.",
    "budget_range": "2.500–3.000€",
    "how_did_you_hear": "Instagram"
  },
  "brief": {
    "wedding_date": "12 Sep 2026",
    "venue": "Costa Brava, exterior platja",
    "garment": "Vestit a mida · Columna minimalista",
    "style": "Columna, escot recte, sense adorns, línia A suau, llarg terra",
    "budget_tier": "Premium · 2.500–3.000€",
    "fabric_notes": "Crep de seda o mikado lleuger (blanc òptic)",
    "extra_notes": "Destination wedding, vol des de París. Necessita vestit que viatgi bé."
  },
  "client_defaults": {
    "name": "Sophie Laurent",
    "wedding_date": "12.09.2026",
    "wedding_date_iso": "2026-09-12",
    "days_until": 143,
    "status": "prospect",
    "garment": "Vestit a mida",
    "garment_style": "Columna minimalista",
    "phone": "+33 6 12 34 56 78",
    "email": "sophie.laurent@mail.fr",
    "notes": "Destination wedding Costa Brava. Minimalista, columna. Via Instagram. 2.500–3.000€"
  }
}
```

- [ ] **Step 1.4: Commit**

```bash
git add backend/data/demo-scenarios/
git commit -m "feat(data): demo scenario JSON files — boho, classic, destination"
```

---

## Task 2: Backend demo route + tests

**Files:**
- Create: `backend/routes/demo.py`
- Create: `backend/tests/test_demo.py`
- Modify: `backend/main.py`

- [ ] **Step 2.1: Write the failing tests**

Create `backend/tests/test_demo.py`:

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
    # summaries only have id + label
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
```

- [ ] **Step 2.2: Run tests to verify they fail**

```bash
cd backend && python -m pytest tests/test_demo.py -v
```

Expected: FAIL with `404` or import errors (route doesn't exist yet)

- [ ] **Step 2.3: Create backend/routes/demo.py**

```python
from fastapi import APIRouter, HTTPException
import json
import os

router = APIRouter(prefix="/demo-scenarios", tags=["demo"])

SCENARIOS_DIR = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "../data/demo-scenarios")
)

def _load(scenario_id: str) -> dict:
    path = os.path.join(SCENARIOS_DIR, f"{scenario_id}.json")
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
```

- [ ] **Step 2.4: Register router in main.py**

Add after the existing imports at the top of `backend/main.py`:
```python
from routes.demo import router as demo_router
```

Add after the existing `app.include_router(events_router)` line:
```python
app.include_router(demo_router)
```

- [ ] **Step 2.5: Run tests to verify they pass**

```bash
cd backend && python -m pytest tests/test_demo.py -v
```

Expected: all 3 tests PASS

- [ ] **Step 2.6: Commit**

```bash
git add backend/routes/demo.py backend/tests/test_demo.py backend/main.py
git commit -m "feat(backend): demo scenarios route — list + get by id"
```

---

## Task 3: Frontend types and API methods

**Files:**
- Modify: `frontend/src/types.ts`
- Modify: `frontend/src/api.ts`

- [ ] **Step 3.1: Add demo types to types.ts**

Append to the end of `frontend/src/types.ts`:

```typescript
export interface DemoScenarioSummary {
  id: string;
  label: string;
}

export interface DemoClientDefaults {
  name: string;
  wedding_date: string;
  wedding_date_iso: string;
  days_until: number;
  status: ClientStatus;
  garment: string;
  garment_style: string;
  phone: string;
  email: string;
  notes: string;
}

export interface DemoScenarioWhatsApp {
  id: string;
  label: string;
  source: 'whatsapp';
  thread: WhatsAppMessage[];
  brief: IntakeBrief;
  client_defaults: DemoClientDefaults;
}

export interface DemoScenarioWebForm {
  id: string;
  label: string;
  source: 'web_form';
  submitted_at: string;
  form_data: Record<string, string>;
  brief: IntakeBrief;
  client_defaults: DemoClientDefaults;
}

export type DemoScenario = DemoScenarioWhatsApp | DemoScenarioWebForm;
```

- [ ] **Step 3.2: Add API methods to api.ts**

In `frontend/src/api.ts`, update the import line at the top to include the new types:

```typescript
import type {
  Client, Fabric, ShoppingItem, IntakeData, ClientBrief, ClientCreate,
  AtelierEvent, AppointmentCreate, DeliveryCreate,
  DemoScenarioSummary, DemoScenario,
} from './types';
```

Then add to the `api` object (after `getBrief`):

```typescript
  listDemoScenarios: () => get<DemoScenarioSummary[]>('/demo-scenarios'),
  getDemoScenario:   (id: string) => get<DemoScenario>(`/demo-scenarios/${id}`),
```

- [ ] **Step 3.3: Commit**

```bash
git add frontend/src/types.ts frontend/src/api.ts
git commit -m "feat(types+api): DemoScenario types + listDemoScenarios/getDemoScenario"
```

---

## Task 4: IntakeDemoScreen component

**Files:**
- Create: `frontend/src/screens/IntakeDemoScreen.tsx`

- [ ] **Step 4.1: Create IntakeDemoScreen.tsx**

```tsx
import { useState, useEffect } from 'react';
import type { DemoScenarioSummary, DemoScenario, DemoScenarioWhatsApp, DemoScenarioWebForm } from '../types';
import { api } from '../api';
import { T } from '../tokens';
import { Label, Mono, Serif } from '../components/primitives';
import { useIsMobile } from '../hooks/useIsMobile';

interface Props {
  onClientCreated: (id: number) => void;
}

// ── WhatsApp thread column ──────────────────────────────────────────────────

function WhatsAppColumn({ scenario }: { scenario: DemoScenarioWhatsApp }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
        <div style={{ width: 8, height: 8, borderRadius: '50%', background: '#25D366' }} />
        <Mono size={10} color={T.ink3}>WhatsApp · Conversa</Mono>
      </div>
      {scenario.thread.map((msg, i) => {
        const isJulia = msg.role === 'julia';
        return (
          <div key={i} style={{ display: 'flex', flexDirection: 'column', alignItems: isJulia ? 'flex-end' : 'flex-start' }}>
            <div style={{
              maxWidth: '80%', padding: '9px 12px',
              background: isJulia ? T.accent : T.paper2,
              color: isJulia ? T.paper : T.ink,
              borderRadius: isJulia ? '12px 12px 2px 12px' : '12px 12px 12px 2px',
              fontFamily: T.sans, fontSize: 13, lineHeight: 1.45,
            }}>{msg.text}</div>
            <Mono size={9} color={T.ink3} style={{ marginTop: 3 }}>{msg.time}</Mono>
          </div>
        );
      })}
    </div>
  );
}

// ── Web form column ─────────────────────────────────────────────────────────

const FORM_LABELS: Record<string, string> = {
  name: 'Nom', email: 'Email', phone: 'Telèfon',
  wedding_date: 'Data boda', venue: 'Lloc',
  style_notes: "Notes d'estil", budget_range: 'Pressupost',
  how_did_you_hear: 'Com ens ha conegut',
};

function WebFormColumn({ scenario }: { scenario: DemoScenarioWebForm }) {
  const date = new Date(scenario.submitted_at).toLocaleDateString('ca-ES', { day: 'numeric', month: 'long', year: 'numeric' });
  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 16 }}>
        <div style={{ fontFamily: T.mono, fontSize: 9, letterSpacing: 0.8, textTransform: 'uppercase' as const, color: T.paper, background: T.ink2, padding: '2px 7px', borderRadius: 999 }}>via web</div>
        <Mono size={10} color={T.ink3}>{date}</Mono>
      </div>
      <div style={{ border: `1px solid ${T.hairline2}`, background: T.paper }}>
        {Object.entries(scenario.form_data).map(([k, v], i, arr) => (
          <div key={k} style={{ display: 'flex', gap: 16, padding: '10px 14px', borderBottom: i < arr.length - 1 ? `1px solid ${T.hairline}` : 'none', flexWrap: 'wrap' as const }}>
            <Mono size={10} color={T.ink3} style={{ width: 120, flexShrink: 0 }}>{FORM_LABELS[k] ?? k}</Mono>
            <div style={{ fontFamily: T.sans, fontSize: 13, color: T.ink, flex: 1 }}>{v}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ── Brief column ────────────────────────────────────────────────────────────

function BriefColumn({ scenario }: { scenario: DemoScenario }) {
  const { brief } = scenario;
  const rows: [string, string][] = [
    ['Data boda', brief.wedding_date],
    ['Lloc', brief.venue],
    ['Peça', brief.garment],
    ['Estil', brief.style],
    ['Pressupost', brief.budget_tier],
    ['Teles', brief.fabric_notes],
  ];
  return (
    <div>
      <Label style={{ marginBottom: 12 }}>Brief extret</Label>
      {rows.map(([k, v]) => v ? (
        <div key={k} style={{ padding: '8px 0', borderBottom: `1px solid ${T.hairline}` }}>
          <Mono size={9} color={T.ink3} style={{ marginBottom: 3 }}>{k}</Mono>
          <div style={{ fontFamily: T.sans, fontSize: 13, color: T.ink, lineHeight: 1.4 }}>{v}</div>
        </div>
      ) : null)}
      {brief.extra_notes && (
        <div style={{ marginTop: 12, padding: '10px 12px', background: T.paper2, borderLeft: `2px solid ${T.gold}` }}>
          <Mono size={9} color={T.ink3} style={{ marginBottom: 4 }}>Notes</Mono>
          <div style={{ fontFamily: T.sans, fontSize: 12, color: T.ink2, lineHeight: 1.5 }}>{brief.extra_notes}</div>
        </div>
      )}
    </div>
  );
}

// ── Client card + action column ─────────────────────────────────────────────

function ClientCardColumn({ scenario, onClientCreated }: { scenario: DemoScenario; onClientCreated: (id: number) => void }) {
  const [creating, setCreating] = useState(false);
  const [created, setCreated] = useState(false);
  const [error, setError] = useState('');
  const { client_defaults: d } = scenario;

  const handleCreate = async () => {
    setCreating(true);
    setError('');
    try {
      const c = await api.createClient({
        name: d.name, wedding_date: d.wedding_date, wedding_date_iso: d.wedding_date_iso,
        days_until: d.days_until, status: d.status, garment: d.garment,
        garment_style: d.garment_style, phone: d.phone, email: d.email, notes: d.notes,
      });
      setCreated(true);
      setTimeout(() => onClientCreated(c.id), 800);
    } catch {
      setError('Error en crear la clienta.');
      setCreating(false);
    }
  };

  return (
    <div>
      <Label style={{ marginBottom: 12 }}>Fitxa proposta</Label>
      <div style={{ border: `1px solid ${T.hairline2}`, padding: '16px' }}>
        <Serif size={20} italic style={{ display: 'block', marginBottom: 12 }}>{d.name}</Serif>
        {([
          ['Boda', d.wedding_date],
          ['Peça', d.garment],
          ['Estil', d.garment_style],
          d.phone ? ['Telèfon', d.phone] : null,
          d.email ? ['Email', d.email] : null,
        ] as ([string, string] | null)[]).filter(Boolean).map(([k, v]) => (
          <div key={k} style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 0', borderBottom: `1px solid ${T.hairline}` }}>
            <Mono size={9} color={T.ink3}>{k}</Mono>
            <Mono size={9} color={T.ink}>{v}</Mono>
          </div>
        ))}
        {d.notes && (
          <div style={{ marginTop: 10, padding: '8px', background: T.paper2 }}>
            <Mono size={9} color={T.ink2}>{d.notes}</Mono>
          </div>
        )}
      </div>
      {error && <Mono size={10} color={T.accent} style={{ marginTop: 8, display: 'block' }}>{error}</Mono>}
      <button
        onClick={handleCreate}
        disabled={creating || created}
        style={{
          width: '100%', marginTop: 16, padding: '14px',
          background: created ? T.accent : creating ? T.ink3 : T.ink,
          color: T.paper, border: 'none',
          fontFamily: T.mono, fontSize: 12, letterSpacing: 0.8,
          textTransform: 'uppercase', cursor: creating || created ? 'not-allowed' : 'pointer',
        }}
      >
        {created ? 'Clienta creada ✓' : creating ? 'Creant…' : 'Crear clienta'}
      </button>
    </div>
  );
}

// ── Main screen ─────────────────────────────────────────────────────────────

export function IntakeDemoScreen({ onClientCreated }: Props) {
  const mobile = useIsMobile();
  const [summaries, setSummaries] = useState<DemoScenarioSummary[]>([]);
  const [selectedId, setSelectedId] = useState('');
  const [scenario, setScenario] = useState<DemoScenario | null>(null);
  const [mobileTab, setMobileTab] = useState<'thread' | 'brief' | 'fitxa'>('thread');
  const px = mobile ? 20 : 40;

  useEffect(() => {
    api.listDemoScenarios().then(list => {
      setSummaries(list);
      if (list.length > 0) setSelectedId(list[0].id);
    });
  }, []);

  useEffect(() => {
    if (!selectedId) return;
    setScenario(null);
    api.getDemoScenario(selectedId).then(setScenario);
  }, [selectedId]);

  const threadCol = scenario
    ? (scenario.source === 'whatsapp'
      ? <WhatsAppColumn scenario={scenario as DemoScenarioWhatsApp} />
      : <WebFormColumn scenario={scenario as DemoScenarioWebForm} />)
    : null;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', overflow: 'hidden' }}>
      {/* Header */}
      <div style={{ padding: `14px ${px}px`, borderBottom: `1px solid ${T.hairline}`, flexShrink: 0, display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 16 }}>
        <Label>06 · Ingrés</Label>
        <select
          value={selectedId}
          onChange={e => setSelectedId(e.target.value)}
          style={{
            border: `1px solid ${T.hairline2}`, background: T.vellum,
            fontFamily: T.mono, fontSize: 10, letterSpacing: 0.6,
            color: T.ink, padding: '6px 10px', outline: 'none', cursor: 'pointer',
          }}
        >
          {summaries.map(s => (
            <option key={s.id} value={s.id}>{s.label}</option>
          ))}
        </select>
      </div>

      {!scenario && (
        <div style={{ padding: 40, fontFamily: T.mono, fontSize: 11, color: T.ink3 }}>Carregant…</div>
      )}

      {scenario && !mobile && (
        /* Desktop 3-column layout */
        <div style={{ flex: 1, display: 'grid', gridTemplateColumns: '42% 32% 26%', overflow: 'hidden' }}>
          <div style={{ overflow: 'auto', padding: '28px 28px 40px', borderRight: `1px solid ${T.hairline}` }}>
            {threadCol}
          </div>
          <div style={{ overflow: 'auto', padding: '28px 28px 40px', borderRight: `1px solid ${T.hairline}` }}>
            <BriefColumn scenario={scenario} />
          </div>
          <div style={{ overflow: 'auto', padding: '28px 24px 40px' }}>
            <ClientCardColumn scenario={scenario} onClientCreated={onClientCreated} />
          </div>
        </div>
      )}

      {scenario && mobile && (
        /* Mobile tab layout */
        <>
          <div style={{ display: 'flex', borderBottom: `1px solid ${T.hairline}`, flexShrink: 0, background: T.paper }}>
            {(['thread', 'brief', 'fitxa'] as const).map(t => {
              const labels = { thread: 'Conversa', brief: 'Brief', fitxa: 'Fitxa' };
              const on = mobileTab === t;
              return (
                <div key={t} onClick={() => setMobileTab(t)} style={{
                  flex: 1, textAlign: 'center', padding: '10px 4px', cursor: 'pointer',
                  position: 'relative', fontFamily: T.serif, fontSize: 15,
                  fontStyle: on ? 'italic' : 'normal', color: on ? T.ink : T.ink3,
                }}>
                  {labels[t]}
                  {on && <div style={{ position: 'absolute', bottom: 0, left: 0, right: 0, height: 2, background: T.accent }} />}
                </div>
              );
            })}
          </div>
          <div style={{ flex: 1, overflow: 'auto', padding: '20px 20px 40px' }}>
            {mobileTab === 'thread' && threadCol}
            {mobileTab === 'brief' && <BriefColumn scenario={scenario} />}
            {mobileTab === 'fitxa' && <ClientCardColumn scenario={scenario} onClientCreated={onClientCreated} />}
          </div>
        </>
      )}
    </div>
  );
}
```

- [ ] **Step 4.2: Commit**

```bash
git add frontend/src/screens/IntakeDemoScreen.tsx
git commit -m "feat(frontend): IntakeDemoScreen — scenario switcher, 3-column layout, create action"
```

---

## Task 5: Wire IntakeDemoScreen into App, Sidebar, MobileHeader

**Files:**
- Modify: `frontend/src/App.tsx`
- Modify: `frontend/src/components/Sidebar.tsx`
- Modify: `frontend/src/components/MobileShell.tsx`

- [ ] **Step 5.1: Update App.tsx**

Change the `Screen` type on line 16:
```tsx
type Screen = 'clients' | 'profile' | 'fabrics' | 'shop' | 'roadmap' | 'intake';
```

Add the import after the existing imports:
```tsx
import { IntakeDemoScreen } from './screens/IntakeDemoScreen';
```

Add the render inside `content` (after the roadmap line):
```tsx
{screen === 'intake' && (
  <IntakeDemoScreen
    onClientCreated={id => {
      refresh().then(() => openClient(id));
    }}
  />
)}
```

- [ ] **Step 5.2: Update Sidebar.tsx**

Change the `Screen` type on line 4:
```tsx
type Screen = 'clients' | 'profile' | 'fabrics' | 'shop' | 'roadmap' | 'intake';
```

Add to the `items` array (after the `roadmap` entry):
```tsx
{ id: 'intake', n: '06', label: 'Ingrés', count: null },
```

- [ ] **Step 5.3: Update MobileShell.tsx**

Change the `Screen` type on line 3:
```tsx
type Screen = 'clients' | 'profile' | 'fabrics' | 'shop' | 'roadmap' | 'intake';
```

Add to the `tabs` array (after the `roadmap` entry):
```tsx
{ id: 'intake', n: '06', label: 'Ingrés' },
```

- [ ] **Step 5.4: Verify end-to-end manually**

```bash
cd frontend && npm run dev
```

1. Check "06 Ingrés" appears in sidebar and mobile tabs
2. Click it → IntakeDemoScreen loads with "Novia Boho" selected by default
3. Switch scenarios via dropdown → thread, brief, client card all update
4. Click "Crear clienta" on any scenario → button shows "Clienta creada ✓" → navigates to that client's profile

- [ ] **Step 5.5: Commit**

```bash
git add frontend/src/App.tsx frontend/src/components/Sidebar.tsx frontend/src/components/MobileShell.tsx
git commit -m "feat(frontend): wire IntakeDemoScreen into App + Sidebar + MobileHeader"
```

---

## Self-Review

**Spec coverage:**
- 3-column desktop layout (thread / brief / client card) ✓
- Mobile tab layout ✓
- Scenario switcher dropdown ✓
- 3 scenarios: boho, classic, destination ✓
- "Crear clienta" button calls POST /clients ✓
- Success state + navigate to profile ✓
- Separate nav item (06 Ingrés) ✓

**Placeholder scan:** All columns have actual rendering code. All types reference back to Task 3. No TBDs.

**Type consistency:** `DemoScenarioWhatsApp` and `DemoScenarioWebForm` are discriminated by `source` field. `WhatsAppColumn` casts to `DemoScenarioWhatsApp` which has `.thread`. `WebFormColumn` casts to `DemoScenarioWebForm` which has `.form_data` and `.submitted_at`. All match.
