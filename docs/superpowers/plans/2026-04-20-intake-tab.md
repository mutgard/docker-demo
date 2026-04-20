# Intake Tab Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an "Ingrés" tab to each client's ProfileScreen showing their intake source (WhatsApp thread or website form submission), extracted brief, and documents.

**Architecture:** Backend serves static JSON files via `GET /clients/{id}/intake`. Frontend adds a two-tab strip ("Fitxa" / "Ingrés") to ProfileScreen and renders `IntakeTab` which switches between a chat bubble view and a form receipt view based on `source`. Demo mode only — no real API calls.

**Tech Stack:** FastAPI (Python), React + TypeScript + Vite, inline styles matching existing token system (`T.*` from `tokens.ts`)

---

## File Map

| Action | Path | Responsibility |
|--------|------|----------------|
| Create | `backend/routes/intake.py` | `GET /clients/{id}/intake` endpoint |
| Modify | `backend/main.py` | Include intake router |
| Create | `backend/data/intake/client_1.json` | Aina Puig — WhatsApp |
| Create | `backend/data/intake/client_2.json` | Berta Soler — Web form |
| Create | `backend/data/intake/client_3.json` | Clara Ferrer — WhatsApp |
| Create | `backend/data/intake/client_4.json` | Dolors Vidal — WhatsApp |
| Create | `backend/data/intake/client_5.json` | Elena Roca — WhatsApp |
| Create | `backend/data/intake/client_6.json` | Fina Batlle — Web form |
| Modify | `frontend/src/types.ts` | IntakeData union type + sub-types |
| Modify | `frontend/src/api.ts` | `getIntake(id)` method |
| Create | `frontend/src/components/IntakeTab.tsx` | WhatsApp + web form views, brief, docs |
| Modify | `frontend/src/screens/ProfileScreen.tsx` | Tab strip + render IntakeTab |

---

## Task 1: Backend endpoint

**Files:**
- Create: `backend/routes/intake.py`
- Modify: `backend/main.py`

- [ ] **Step 1: Create the intake router**

Create `backend/routes/intake.py`:

```python
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
```

- [ ] **Step 2: Register the router in main.py**

In `backend/main.py`, add after the existing router imports:

```python
from routes.intake import router as intake_router
```

And after the existing `app.include_router` calls:

```python
app.include_router(intake_router)
```

- [ ] **Step 3: Create data directory**

```bash
mkdir -p backend/data/intake
```

- [ ] **Step 4: Verify endpoint responds**

Start the backend:
```bash
cd backend && uvicorn main:app --reload --port 8000
```

Before adding JSON files, confirm 404 is returned:
```bash
curl -s http://localhost:8000/clients/1/intake
# Expected: {"detail":"No intake data for this client"}
```

- [ ] **Step 5: Commit**

```bash
git add backend/routes/intake.py backend/main.py
git commit -m "feat(backend): GET /clients/{id}/intake endpoint"
```

---

## Task 2: Mock JSON data for all 6 clients

**Files:**
- Create: `backend/data/intake/client_1.json` through `client_6.json`

- [ ] **Step 1: Create client_1.json (Aina Puig — WhatsApp)**

Create `backend/data/intake/client_1.json`:

```json
{
  "source": "whatsapp",
  "thread": [
    {"role": "client", "text": "Hola! M'han recomanat el teu atelier. Estic buscant vestit de núvia per al 17 de maig.", "time": "12 Gen 11:23"},
    {"role": "julia", "text": "Hola Aina! Quina il·lusió. Tens alguna idea de l'estil que busques?", "time": "12 Gen 11:31"},
    {"role": "client", "text": "Sí, ho tinc bastant clar! Vull escot en V molt pronunciat, estil princesa però modern. I que pugui ballar tota la nit!", "time": "12 Gen 11:45"},
    {"role": "julia", "text": "M'encanta que ho tinguis clar! El mikado és perfecte per l'estructura princesa i aguanta molt bé el moviment. Quants convidats teniu?", "time": "12 Gen 12:02"},
    {"role": "client", "text": "Uns 120. Cerimònia a l'aire lliure i sopar en masia.", "time": "12 Gen 12:08"},
    {"role": "julia", "text": "Perfecte per un vestit amb volum a la falda. Et proposo mikado seda per al cos i tul de vol per la faldilla. Vols mànigues?", "time": "12 Gen 12:15"},
    {"role": "client", "text": "No, sense mànigues. I m'agradaria un detall de puntilla a l'escot.", "time": "12 Gen 12:22"},
    {"role": "julia", "text": "Puntilla Chantilly a l'escot quedarà sublim. Quin pressupost tens en ment?", "time": "12 Gen 12:30"},
    {"role": "client", "text": "Entre 2.000 i 2.500€.", "time": "12 Gen 12:33"},
    {"role": "julia", "text": "Podem treballar perfectament dins d'aquest pressupost. Et proposo quedar per prendre mides i ensenyar-te mostres de tela. Quan et va bé?", "time": "12 Gen 12:40"}
  ],
  "brief": {
    "wedding_date": "17 Mai 2026",
    "venue": "Masia, cerimònia a l'aire lliure",
    "garment": "Vestit a mida · Princesa modern",
    "style": "Escot en V profund, sense mànigues, puntilla Chantilly a l'escot, faldilla amb volum",
    "budget_tier": "Standard",
    "fabric_notes": "Mikado seda marfil (cos), tul francès (vel), puntilla Chantilly (vora)",
    "extra_notes": "Ha de poder ballar. 120 convidats."
  },
  "documents": []
}
```

- [ ] **Step 2: Create client_2.json (Berta Soler — Web form)**

Create `backend/data/intake/client_2.json`:

```json
{
  "source": "web_form",
  "submitted_at": "2026-01-18",
  "form_data": {
    "name": "Berta Soler",
    "email": "berta.soler@gmail.com",
    "phone": "+34 612 88 31 04",
    "wedding_date": "31 de maig de 2026",
    "venue": "Monestir de Pedralbes, Barcelona",
    "style_notes": "Busco un vestit romàntic i clàssic, amb vel llarg. M'inspira molt l'estètica de les núvies dels anys 50. Voldria algun detall de botons a l'esquena.",
    "budget_range": "2.000 – 3.000 €",
    "how_did_you_hear": "Instagram (@juliette.atelier)"
  },
  "brief": {
    "wedding_date": "31 Mai 2026",
    "venue": "Monestir de Pedralbes, Barcelona",
    "garment": "Vestit + vel · Romàntic clàssic",
    "style": "Estètica anys 50, botons a l'esquena, vel llarg",
    "budget_tier": "Standard",
    "fabric_notes": "Per definir — primera visita pendent",
    "extra_notes": "Contacte via Instagram. Primera consulta feta el 10 d'abril."
  },
  "documents": []
}
```

- [ ] **Step 3: Create client_3.json (Clara Ferrer — WhatsApp)**

Create `backend/data/intake/client_3.json`:

```json
{
  "source": "whatsapp",
  "thread": [
    {"role": "client", "text": "Bona tarda! Soc la Clara, em recomana la Montse Valls. Necessito un vestit de princesa molt estructurat per al 14 de juny.", "time": "15 Nov 11:05"},
    {"role": "julia", "text": "Hola Clara! La Montse és una clienta molt especial. Estructura real és la meva especialitat. Tens referències?", "time": "15 Nov 11:18"},
    {"role": "client", "text": "Sí, mira [foto1.jpg] [foto2.jpg] [foto3.jpg] M'agrada molt la silueta de Kate Middleton i Grace Kelly.", "time": "15 Nov 11:25"},
    {"role": "julia", "text": "Meravelloses referències. Cor estructurat, faldilla amb múltiples capes d'organza. Serà una feina preciosa. Lloc de cerimònia?", "time": "15 Nov 11:42"},
    {"role": "client", "text": "Catedral de Girona. Vull que sigui imponent.", "time": "15 Nov 11:45"},
    {"role": "julia", "text": "Catedral mereix un vestit catedral! Mikado per al cos amb organza de seda per als volants. Quants metres de cua vols?", "time": "15 Nov 12:00"},
    {"role": "client", "text": "Com més llarga millor. I vull puntilla a l'escot. Pressupost no és problema, vull el millor.", "time": "15 Nov 12:08"},
    {"role": "julia", "text": "Entès. Treballarem amb els millors materials de Gratacós. Et proposo prendre mides la primera setmana de desembre.", "time": "15 Nov 12:15"},
    {"role": "client", "text": "Perfecte. Puc venir el dimecres 4 de desembre a les 11h?", "time": "15 Nov 12:20"},
    {"role": "julia", "text": "Apuntat! T'envio confirmació per email. Fins aviat, Clara.", "time": "15 Nov 12:22"},
    {"role": "client", "text": "Gràcies! Tinc moltes ganes.", "time": "15 Nov 12:23"},
    {"role": "julia", "text": "Nosaltres també! Serà un vestit extraordinari.", "time": "15 Nov 12:25"}
  ],
  "brief": {
    "wedding_date": "14 Jun 2026",
    "venue": "Catedral de Girona",
    "garment": "Vestit princesa · Royal / estructura",
    "style": "Silueta Kate Middleton / Grace Kelly, cos estructurat, escot amb puntilla, cua llarga, volants d'organza",
    "budget_tier": "Couture",
    "fabric_notes": "Mikado seda marfil (cos), organza de seda (volants), tul de cotó (enagua), puntilla Chantilly (escot), entretela fusible (estructura)",
    "extra_notes": "Referència Montse Valls. Qualitat sense límit de pressupost."
  },
  "documents": []
}
```

- [ ] **Step 4: Create client_4.json (Dolors Vidal — WhatsApp)**

Create `backend/data/intake/client_4.json`:

```json
{
  "source": "whatsapp",
  "thread": [
    {"role": "client", "text": "Hola! He vist el vostre Instagram i m'ha encantat. Estic buscant vestit per al 28 de juny però no tinc massa clar l'estil...", "time": "08 Feb 10:12"},
    {"role": "julia", "text": "Hola Dolors! Perfecte, per aquí comencem. Tens alguna foto o referència que t'agradi, encara que sigui molt diferent?", "time": "08 Feb 10:25"},
    {"role": "client", "text": "T'envio algunes de Pinterest [foto1.jpg] [foto2.jpg] [foto3.jpg] [foto4.jpg] Sé que algunes son molt diferents entre elles jaja", "time": "08 Feb 10:31"},
    {"role": "julia", "text": "No passa res! Veig que t'agraden les línies fluixes i els detalls romàntics. Una cosa important: cotilla o sense?", "time": "08 Feb 10:45"},
    {"role": "client", "text": "SENSE cotilla per favor. He portat tota la vida i ja estic farta!", "time": "08 Feb 10:47"},
    {"role": "julia", "text": "Entès perfectament! Podem fer un cos fluid molt elegant sense estructura. On serà la boda?", "time": "08 Feb 10:55"},
    {"role": "client", "text": "A una masia del Maresme, jardí exterior. Casual-elegant, res de molt pompós.", "time": "08 Feb 11:02"},
    {"role": "julia", "text": "M'encanta. Et proposo una primera visita sense compromís per veure mostres i parlar d'estil. Tens alguna data disponible a finals d'abril?", "time": "08 Feb 11:10"}
  ],
  "brief": {
    "wedding_date": "28 Jun 2026",
    "venue": "Masia del Maresme, jardí exterior",
    "garment": "Consulta inicial · Estil per definir",
    "style": "Línies fluixes, romàntic, sense cotilla ni estructura. Ambient casual-elegant.",
    "budget_tier": "Standard",
    "fabric_notes": "Per definir — primera visita el 22 d'abril",
    "extra_notes": "Porta Pinterest. Molt oberta a suggeriments. Sense cotilla: innegociable."
  },
  "documents": []
}
```

- [ ] **Step 5: Create client_5.json (Elena Roca — WhatsApp)**

Create `backend/data/intake/client_5.json`:

```json
{
  "source": "whatsapp",
  "thread": [
    {"role": "client", "text": "Hola Juliette! Soc l'Elena, ens vam conèixer al mercat de Santa Caterina l'estiu passat.", "time": "20 Gen 16:33"},
    {"role": "julia", "text": "Elena! Quina alegria! Recordo perfectament. Et cases??", "time": "20 Gen 16:45"},
    {"role": "client", "text": "Sí!! El 5 de juliol. Vull alguna cosa teva, saps que m'encanta com treballes.", "time": "20 Gen 16:47"},
    {"role": "julia", "text": "Quina emoció fer el teu vestit! Explica'm... Boda gran o petita?", "time": "20 Gen 16:52"},
    {"role": "client", "text": "Petita, 40 persones, finca a l'Empordà. Vull alguna cosa fresca, natural, res de formal. Ja saps el meu estil.", "time": "20 Gen 16:58"},
    {"role": "julia", "text": "Perfectament! Gasa de cotó, potser amb un detall de puntilla italiana a les mànigues llargues. Fluix i elegant. Pressupost?", "time": "20 Gen 17:05"},
    {"role": "client", "text": "Fins a 1.500€, soc mestra. Però sé que amb tu quedarà preciós.", "time": "20 Gen 17:08"},
    {"role": "julia", "text": "Treballem perfectament! Confia en mi, et faré el vestit de somni. Quedem la setmana vinent?", "time": "20 Gen 17:12"}
  ],
  "brief": {
    "wedding_date": "05 Jul 2026",
    "venue": "Finca a l'Empordà",
    "garment": "Vestit bohemi · Fluix / natural",
    "style": "Fluid, fresc, natural. Puntilla italiana a les mànigues llargues. Res de formal.",
    "budget_tier": "Standard",
    "fabric_notes": "Gasa de cotó (cos), puntilla italiana (màniga), setí de seda (cinturó)",
    "extra_notes": "Clienta coneguda personalment. Confiança total. Boda íntima 40 persones."
  },
  "documents": []
}
```

- [ ] **Step 6: Create client_6.json (Fina Batlle — Web form)**

Create `backend/data/intake/client_6.json`:

```json
{
  "source": "web_form",
  "submitted_at": "2024-09-05",
  "form_data": {
    "name": "Fina Batlle",
    "email": "fina.batlle@yahoo.es",
    "phone": "+34 634 77 23 91",
    "wedding_date": "12 de setembre de 2025",
    "venue": "Hotel Arts, Barcelona",
    "style_notes": "Busco un vestit sirena molt glamurós, amb escot molt obert a l'esquena. M'agraden els botons de perla. Referència: Zuhair Murad però assequible.",
    "budget_range": "2.500 – 3.500 €",
    "how_did_you_hear": "Recomanació d'una amiga (Núria Pla)"
  },
  "brief": {
    "wedding_date": "12 Set 2025",
    "venue": "Hotel Arts, Barcelona",
    "garment": "Vestit sirena · Glamour / escot obert",
    "style": "Silueta sirena, escot profund a l'esquena, botons de perla, glamurós",
    "budget_tier": "Premium",
    "fabric_notes": "Crepe de seda (cos), tul elàstic (folre)",
    "extra_notes": "Vestit entregat i clienta molt satisfeta. Referència Zuhair Murad. Via recomanació Núria Pla."
  },
  "documents": []
}
```

- [ ] **Step 7: Verify endpoint returns data**

With the backend still running:
```bash
curl -s http://localhost:8000/clients/1/intake | python3 -m json.tool | head -20
# Expected: JSON with "source": "whatsapp" and "thread" array

curl -s http://localhost:8000/clients/2/intake | python3 -m json.tool | head -10
# Expected: JSON with "source": "web_form" and "form_data" object
```

- [ ] **Step 8: Commit**

```bash
git add backend/data/
git commit -m "feat(data): mock intake JSON for all 6 clients"
```

---

## Task 3: TypeScript types + API method

**Files:**
- Modify: `frontend/src/types.ts`
- Modify: `frontend/src/api.ts`

- [ ] **Step 1: Add intake types to types.ts**

At the end of `frontend/src/types.ts`, append:

```ts
export interface IntakeBrief {
  wedding_date: string;
  venue: string;
  garment: string;
  style: string;
  budget_tier: string;
  fabric_notes: string;
  extra_notes: string;
}

export interface IntakeDocument {
  label: string;
  type: string;
  url: string | null;
}

export interface WhatsAppMessage {
  role: 'client' | 'julia';
  text: string;
  time: string;
}

export interface WhatsAppIntake {
  source: 'whatsapp';
  thread: WhatsAppMessage[];
  brief: IntakeBrief;
  documents: IntakeDocument[];
}

export interface WebFormIntake {
  source: 'web_form';
  submitted_at: string;
  form_data: Record<string, string>;
  brief: IntakeBrief;
  documents: IntakeDocument[];
}

export type IntakeData = WhatsAppIntake | WebFormIntake;
```

- [ ] **Step 2: Add getIntake to api.ts**

In `frontend/src/api.ts`, add the import at the top (update the existing import line):

```ts
import type { Client, Fabric, ShoppingItem, IntakeData } from './types';
```

Then add to the `api` object:

```ts
getIntake: async (id: number): Promise<IntakeData | null> => {
  const r = await fetch(`${BASE}/clients/${id}/intake`);
  if (r.status === 404) return null;
  if (!r.ok) throw new Error(`GET /clients/${id}/intake → ${r.status}`);
  return r.json();
},
```

- [ ] **Step 3: Verify TypeScript compiles**

```bash
cd frontend && npx tsc --noEmit
# Expected: no errors
```

- [ ] **Step 4: Commit**

```bash
git add frontend/src/types.ts frontend/src/api.ts
git commit -m "feat(types): IntakeData types + getIntake API method"
```

---

## Task 4: IntakeTab component

**Files:**
- Create: `frontend/src/components/IntakeTab.tsx`

- [ ] **Step 1: Create IntakeTab.tsx**

Create `frontend/src/components/IntakeTab.tsx`:

```tsx
import { useState, useEffect } from 'react';
import type { IntakeData, WhatsAppIntake, WebFormIntake, IntakeBrief } from '../types';
import { api } from '../api';
import { T } from '../tokens';
import { Label, Mono, Rule } from './primitives';
import { useIsMobile } from '../hooks/useIsMobile';

const FORM_LABELS: Record<string, string> = {
  name: 'Nom',
  email: 'Email',
  phone: 'Telèfon',
  wedding_date: 'Data boda',
  venue: 'Lloc',
  style_notes: 'Notes d\'estil',
  budget_range: 'Pressupost',
  how_did_you_hear: 'Com ens ha conegut',
};

function BriefPanel({ brief }: { brief: IntakeBrief }) {
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
      <Label style={{ marginBottom: 12 }}>Resum</Label>
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

function WhatsAppView({ intake }: { intake: WhatsAppIntake }) {
  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 16 }}>
        <div style={{ width: 8, height: 8, borderRadius: '50%', background: '#25D366' }} />
        <Mono size={10} color={T.ink3}>WhatsApp</Mono>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
        {intake.thread.map((msg, i) => {
          const isJulia = msg.role === 'julia';
          return (
            <div key={i} style={{ display: 'flex', flexDirection: 'column', alignItems: isJulia ? 'flex-end' : 'flex-start' }}>
              <div style={{
                maxWidth: '78%',
                padding: '9px 12px',
                background: isJulia ? T.accent : T.paper2,
                color: isJulia ? T.paper : T.ink,
                borderRadius: isJulia ? '12px 12px 2px 12px' : '12px 12px 12px 2px',
                fontFamily: T.sans,
                fontSize: 13,
                lineHeight: 1.45,
              }}>
                {msg.text}
              </div>
              <Mono size={9} color={T.ink3} style={{ marginTop: 3 }}>{msg.time}</Mono>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function WebFormView({ intake }: { intake: WebFormIntake }) {
  const date = new Date(intake.submitted_at).toLocaleDateString('ca-ES', { day: 'numeric', month: 'long', year: 'numeric' });
  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 16 }}>
        <div style={{ fontFamily: T.mono, fontSize: 9, letterSpacing: 0.8, textTransform: 'uppercase', color: T.paper, background: T.ink2, padding: '2px 7px', borderRadius: 999 }}>via web</div>
        <Mono size={10} color={T.ink3}>{date}</Mono>
      </div>
      <div style={{ border: `1px solid ${T.hairline2}`, background: T.paper }}>
        {Object.entries(intake.form_data).map(([k, v], i, arr) => (
          <div key={k} style={{ display: 'flex', gap: 16, padding: '10px 14px', borderBottom: i < arr.length - 1 ? `1px solid ${T.hairline}` : 'none', flexWrap: 'wrap' }}>
            <Mono size={10} color={T.ink3} style={{ width: 120, flexShrink: 0 }}>{FORM_LABELS[k] ?? k}</Mono>
            <div style={{ fontFamily: T.sans, fontSize: 13, color: T.ink, flex: 1 }}>{v}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

export function IntakeTab({ clientId }: { clientId: number }) {
  const [data, setData] = useState<IntakeData | null | 'loading'>('loading');
  const mobile = useIsMobile();

  useEffect(() => {
    api.getIntake(clientId).then(setData);
  }, [clientId]);

  if (data === 'loading') {
    return <div style={{ padding: 40, fontFamily: T.mono, fontSize: 11, color: T.ink3 }}>Carregant…</div>;
  }

  if (data === null) {
    return (
      <div style={{ padding: 40, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8 }}>
        <Mono size={11} color={T.ink3}>Sense dades d'ingrés</Mono>
      </div>
    );
  }

  const sourceView = data.source === 'whatsapp'
    ? <WhatsAppView intake={data} />
    : <WebFormView intake={data} />;

  if (mobile) {
    return (
      <div style={{ padding: '20px 20px 40px', display: 'flex', flexDirection: 'column', gap: 28 }}>
        {sourceView}
        <Rule />
        <BriefPanel brief={data.brief} />
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', height: '100%', gap: 0 }}>
      <div style={{ flex: '0 0 60%', padding: '28px 32px 40px', overflowY: 'auto', borderRight: `1px solid ${T.hairline}` }}>
        {sourceView}
      </div>
      <div style={{ flex: 1, padding: '28px 32px 40px', overflowY: 'auto' }}>
        <BriefPanel brief={data.brief} />
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Verify TypeScript compiles**

```bash
cd frontend && npx tsc --noEmit
# Expected: no errors
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/IntakeTab.tsx
git commit -m "feat(ui): IntakeTab component — WhatsApp thread + web form views"
```

---

## Task 5: ProfileScreen tab strip

**Files:**
- Modify: `frontend/src/screens/ProfileScreen.tsx`

- [ ] **Step 1: Add tab state and imports**

At the top of `frontend/src/screens/ProfileScreen.tsx`, add to the existing imports:

```ts
import { IntakeTab } from '../components/IntakeTab';
```

Inside `ProfileScreen`, after `const px = mobile ? 20 : 40;`, add:

```ts
const [tab, setTab] = useState<'fitxa' | 'ingres'>('fitxa');
```

- [ ] **Step 2: Add tab strip between hero and scrollable content**

In the JSX, between the hero `</div>` and the scrollable content `<div style={{ flex: 1, overflow: 'auto'...`, insert:

```tsx
{/* Tab strip */}
<div style={{ display: 'flex', borderBottom: `1px solid ${T.hairline}`, flexShrink: 0, background: T.paper }}>
  {(['fitxa', 'ingres'] as const).map((t) => {
    const labels = { fitxa: 'Fitxa', ingres: 'Ingrés' };
    const on = tab === t;
    return (
      <div
        key={t}
        onClick={() => setTab(t)}
        style={{
          padding: '10px 20px',
          cursor: 'pointer',
          position: 'relative',
          fontFamily: T.serif,
          fontSize: 15,
          fontStyle: on ? 'italic' : 'normal',
          color: on ? T.ink : T.ink3,
        }}
      >
        {labels[t]}
        {on && (
          <div style={{ position: 'absolute', bottom: 0, left: 0, right: 0, height: 2, background: T.accent }} />
        )}
      </div>
    );
  })}
</div>
```

- [ ] **Step 3: Wrap existing content in Fitxa tab, add Ingrés tab**

Replace the scrollable content block:

```tsx
{/* Scrollable content — Fitxa tab */}
<div style={{ flex: 1, overflow: 'auto', padding: `${mobile ? 20 : 28}px ${px}px 40px`, display: tab === 'fitxa' ? 'block' : 'none' }}>
  {/* ... existing content unchanged ... */}
</div>

{/* Ingrés tab */}
{tab === 'ingres' && (
  <div style={{ flex: 1, minHeight: 0, overflow: 'auto', display: 'flex', flexDirection: 'column' }}>
    <IntakeTab clientId={c.id} />
  </div>
)}
```

Note: use `display: 'none'` on the Fitxa panel rather than unmounting it so scroll position is preserved when switching back.

- [ ] **Step 4: Verify TypeScript compiles**

```bash
cd frontend && npx tsc --noEmit
# Expected: no errors
```

- [ ] **Step 5: Manual smoke test**

Start both backend and frontend:
```bash
# Terminal 1
cd backend && uvicorn main:app --reload --port 8000

# Terminal 2
cd frontend && npm run dev
```

Open http://localhost:5173. Click a client. Verify:
- "Fitxa" and "Ingrés" tabs appear below the hero
- "Fitxa" shows existing profile content (unchanged)
- "Ingrés" on a WhatsApp client (e.g. Aina, id=1) shows chat bubbles + brief panel
- "Ingrés" on a web form client (e.g. Berta, id=2) shows form receipt + brief panel
- Mobile view: single column, source view then brief stacked

- [ ] **Step 6: Commit**

```bash
git add frontend/src/screens/ProfileScreen.tsx
git commit -m "feat(ui): Fitxa/Ingrés tab strip in ProfileScreen"
```

---

## Task 6: Push to Railway

- [ ] **Step 1: Push**

```bash
git push origin master
```

- [ ] **Step 2: Verify Railway deploy**

Watch Railway dashboard for build success. Once deployed, open the production URL, navigate to a client profile, and verify the Ingrés tab works with live data from the backend.
