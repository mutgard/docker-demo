# Client Brief (Shareable) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give each client a shareable brief link Julia can copy and send to the bride — a token-based public URL that renders a beautiful standalone page with the dress proposal.

**Architecture:** Each intake JSON gets `token` + `client_name` fields. A new `GET /brief/:token` backend endpoint scans intake files, finds the match, and returns bride-safe fields. A new standalone `BriefPage` component renders at `/brief/:token` (detected via `window.location.pathname` in App.tsx). A "Copiar link" button in the ProfileScreen back bar fetches the token and copies the URL to clipboard.

**Tech Stack:** FastAPI (Python), React + TypeScript + Vite, navigator.clipboard API, inline styles with T.* token system

---

## File Map

| Action | Path | Responsibility |
|--------|------|----------------|
| Modify | `backend/data/intake/client_1.json` – `client_6.json` | Add `token` + `client_name` fields |
| Create | `backend/routes/brief.py` | `GET /brief/:token` endpoint |
| Modify | `backend/main.py` | Include brief router |
| Modify | `frontend/src/types.ts` | Add `token?: string` to intake types + `ClientBrief` interface |
| Modify | `frontend/src/api.ts` | Add `getBrief(token)` method |
| Create | `frontend/src/pages/BriefPage.tsx` | Standalone bride-facing brief page |
| Modify | `frontend/src/App.tsx` | Pathname check → render BriefPage |
| Modify | `frontend/src/screens/ProfileScreen.tsx` | "Copiar link" button in back bar |

---

## Task 1: Add token + client_name to intake JSONs

**Files:**
- Modify: `backend/data/intake/client_1.json` through `client_6.json`

- [ ] **Step 1: Add fields to client_1.json**

Open `backend/data/intake/client_1.json`. Add two fields at the top level, directly after the opening `{`:

```json
{
  "token": "tok_aina_a3f9k2",
  "client_name": "Aina Puig",
  "source": "whatsapp",
  ...
}
```

- [ ] **Step 2: Add fields to client_2.json**

```json
{
  "token": "tok_berta_m7p4n8",
  "client_name": "Berta Soler",
  "source": "web_form",
  ...
}
```

- [ ] **Step 3: Add fields to client_3.json**

```json
{
  "token": "tok_clara_z2x8v5",
  "client_name": "Clara Ferrer",
  "source": "whatsapp",
  ...
}
```

- [ ] **Step 4: Add fields to client_4.json**

```json
{
  "token": "tok_dolors_k9q1w3",
  "client_name": "Dolors Vidal",
  "source": "whatsapp",
  ...
}
```

- [ ] **Step 5: Add fields to client_5.json**

```json
{
  "token": "tok_elena_r6t0j7",
  "client_name": "Elena Roca",
  "source": "whatsapp",
  ...
}
```

- [ ] **Step 6: Add fields to client_6.json**

```json
{
  "token": "tok_fina_b4y2s9",
  "client_name": "Fina Batlle",
  "source": "web_form",
  ...
}
```

- [ ] **Step 7: Validate all 6 files parse correctly**

```bash
cd /Users/roger/Documents/docker-demo
for i in 1 2 3 4 5 6; do
  python3 -c "
import json
d = json.load(open('backend/data/intake/client_$i.json'))
assert 'token' in d, 'missing token'
assert 'client_name' in d, 'missing client_name'
print(f'client_$i: token={d[\"token\"]}, name={d[\"client_name\"]}')
"
done
```

Expected output:
```
client_1: token=tok_aina_a3f9k2, name=Aina Puig
client_2: token=tok_berta_m7p4n8, name=Berta Soler
client_3: token=tok_clara_z2x8v5, name=Clara Ferrer
client_4: token=tok_dolors_k9q1w3, name=Dolors Vidal
client_5: token=tok_elena_r6t0j7, name=Elena Roca
client_6: token=tok_fina_b4y2s9, name=Fina Batlle
```

- [ ] **Step 8: Commit**

```bash
cd /Users/roger/Documents/docker-demo
git add backend/data/intake/
git commit -m "feat(data): add brief token + client_name to intake files"
```

---

## Task 2: Backend brief endpoint

**Files:**
- Create: `backend/routes/brief.py`
- Modify: `backend/main.py`

- [ ] **Step 1: Create backend/routes/brief.py**

Create `/Users/roger/Documents/docker-demo/backend/routes/brief.py`:

```python
from fastapi import APIRouter, HTTPException
import json
import os
import glob

router = APIRouter(prefix="/brief", tags=["brief"])

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
```

- [ ] **Step 2: Register the router in main.py**

In `/Users/roger/Documents/docker-demo/backend/main.py`, add after the existing router imports:

```python
from routes.brief import router as brief_router
```

And after the existing `app.include_router` calls (before the static file mount):

```python
app.include_router(brief_router)
```

The final `app.include_router` block should look like:

```python
app.include_router(clients_router)
app.include_router(fabrics_router)
app.include_router(shopping_router)
app.include_router(intake_router)
app.include_router(brief_router)
```

- [ ] **Step 3: Verify syntax**

```bash
cd /Users/roger/Documents/docker-demo/backend && python3 -c "import routes.brief; print('OK')"
```

Expected: `OK`

- [ ] **Step 4: Smoke test the endpoint**

Start the backend:
```bash
cd /Users/roger/Documents/docker-demo/backend && uvicorn main:app --reload --port 8000
```

In another terminal:
```bash
curl -s http://localhost:8000/brief/tok_aina_a3f9k2 | python3 -m json.tool
```

Expected:
```json
{
    "client_name": "Aina Puig",
    "wedding_date": "17 Mai 2026",
    "venue": "Masia, cerim\u00f2nia a l'aire lliure",
    "garment": "Vestit a mida \u00b7 Princesa modern",
    "style": "Escot en V profund, sense m\u00e0nigues, puntilla Chantilly a l'escot, faldilla amb volum",
    "fabric_notes": "Mikado seda marfil (cos), tul franc\u00e8s (vel), puntilla Chantilly (vora)"
}
```

Also test a bad token returns 404:
```bash
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/brief/invalid_token
```
Expected: `404`

- [ ] **Step 5: Commit**

```bash
cd /Users/roger/Documents/docker-demo
git add backend/routes/brief.py backend/main.py
git commit -m "feat(backend): GET /brief/:token endpoint"
```

---

## Task 3: TypeScript types + API method

**Files:**
- Modify: `frontend/src/types.ts`
- Modify: `frontend/src/api.ts`

- [ ] **Step 1: Add token field to intake types in types.ts**

In `/Users/roger/Documents/docker-demo/frontend/src/types.ts`, add `token?: string` to both `WhatsAppIntake` and `WebFormIntake`:

Current `WhatsAppIntake`:
```ts
export interface WhatsAppIntake {
  source: 'whatsapp';
  thread: WhatsAppMessage[];
  brief: IntakeBrief;
  documents: IntakeDocument[];
}
```

Replace with:
```ts
export interface WhatsAppIntake {
  source: 'whatsapp';
  token?: string;
  thread: WhatsAppMessage[];
  brief: IntakeBrief;
  documents: IntakeDocument[];
}
```

Current `WebFormIntake`:
```ts
export interface WebFormIntake {
  source: 'web_form';
  submitted_at: string;
  form_data: Record<string, string>;
  brief: IntakeBrief;
  documents: IntakeDocument[];
}
```

Replace with:
```ts
export interface WebFormIntake {
  source: 'web_form';
  token?: string;
  submitted_at: string;
  form_data: Record<string, string>;
  brief: IntakeBrief;
  documents: IntakeDocument[];
}
```

- [ ] **Step 2: Add ClientBrief interface to types.ts**

At the end of `frontend/src/types.ts`, append:

```ts
export interface ClientBrief {
  client_name: string;
  wedding_date: string;
  venue: string;
  garment: string;
  style: string;
  fabric_notes: string;
}
```

- [ ] **Step 3: Add getBrief to api.ts**

In `/Users/roger/Documents/docker-demo/frontend/src/api.ts`, update the import line:

```ts
import type { Client, Fabric, ShoppingItem, IntakeData, ClientBrief } from './types';
```

Then add to the `api` object (after `getIntake`):

```ts
getBrief: async (token: string): Promise<ClientBrief | null> => {
  const r = await fetch(`${BASE}/brief/${token}`);
  if (r.status === 404) return null;
  if (!r.ok) throw new Error(`GET /brief/${token} → ${r.status}`);
  return r.json();
},
```

- [ ] **Step 4: Verify TypeScript compiles**

```bash
cd /Users/roger/Documents/docker-demo/frontend && npx tsc --noEmit 2>&1
```

Expected: no errors

- [ ] **Step 5: Commit**

```bash
cd /Users/roger/Documents/docker-demo
git add frontend/src/types.ts frontend/src/api.ts
git commit -m "feat(types): ClientBrief type + getBrief API method"
```

---

## Task 4: BriefPage component

**Files:**
- Create: `frontend/src/pages/BriefPage.tsx`

- [ ] **Step 1: Create the pages directory and BriefPage.tsx**

Create `/Users/roger/Documents/docker-demo/frontend/src/pages/BriefPage.tsx`:

```tsx
import { useState, useEffect } from 'react';
import type { ClientBrief } from '../types';
import { api } from '../api';
import { T } from '../tokens';

export function BriefPage({ token }: { token: string }) {
  const [brief, setBrief] = useState<ClientBrief | null | 'loading'>('loading');

  useEffect(() => {
    api.getBrief(token)
      .then(setBrief)
      .catch(() => setBrief(null));
  }, [token]);

  if (brief === 'loading') {
    return <div style={{ minHeight: '100dvh', background: T.paper }} />;
  }

  if (brief === null) {
    return (
      <div style={{
        minHeight: '100dvh', background: T.paper,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        fontFamily: T.mono, fontSize: 11, letterSpacing: 1.2,
        textTransform: 'uppercase', color: T.ink3,
      }}>
        Aquest link no és vàlid.
      </div>
    );
  }

  const rows: [string, string][] = [
    ['Lloc', brief.venue],
    ['Peça', brief.garment],
    ['Estil', brief.style],
    ['Teles', brief.fabric_notes],
  ];

  return (
    <div style={{ minHeight: '100dvh', background: T.paper, color: T.ink, fontFamily: T.sans }}>
      <div style={{ maxWidth: 680, margin: '0 auto', padding: '48px 28px 80px' }}>

        {/* Atelier header */}
        <div style={{ textAlign: 'center', marginBottom: 40 }}>
          <div style={{ display: 'inline-flex', alignItems: 'baseline', gap: 6 }}>
            <span style={{ fontFamily: T.serif, fontSize: 22, color: T.ink, lineHeight: 1 }}>Juliette</span>
            <span style={{ fontFamily: T.serif, fontSize: 22, fontStyle: 'italic', color: T.gold, lineHeight: 1 }}>Atelier</span>
          </div>
          <div style={{ height: 1, background: T.hairline, marginTop: 16 }} />
        </div>

        {/* Hero */}
        <div style={{ textAlign: 'center', marginBottom: 52 }}>
          <div style={{
            fontFamily: T.serif, fontSize: 44, fontStyle: 'italic',
            lineHeight: 1.1, letterSpacing: -0.5, color: T.ink,
          }}>
            {brief.client_name}
          </div>
          <div style={{
            fontFamily: T.mono, fontSize: 11, letterSpacing: 1.2,
            textTransform: 'uppercase', color: T.ink3, marginTop: 12,
          }}>
            Proposta · {brief.wedding_date}
          </div>
        </div>

        {/* Brief rows */}
        <div>
          {rows.map(([label, value]) => (
            <div key={label} style={{ padding: '20px 0', borderTop: `1px solid ${T.hairline}` }}>
              <div style={{
                fontFamily: T.mono, fontSize: 9, letterSpacing: 1.2,
                textTransform: 'uppercase', color: T.ink3, marginBottom: 8,
              }}>
                {label}
              </div>
              <div style={{ fontFamily: T.sans, fontSize: 15, color: T.ink, lineHeight: 1.65 }}>
                {value}
              </div>
            </div>
          ))}
          <div style={{ borderTop: `1px solid ${T.hairline}` }} />
        </div>

        {/* Footer */}
        <div style={{ textAlign: 'center', marginTop: 56 }}>
          <div style={{
            fontFamily: T.mono, fontSize: 10, letterSpacing: 0.8,
            textTransform: 'uppercase', color: T.ink3,
          }}>
            Juliette Atelier
          </div>
        </div>

      </div>
    </div>
  );
}
```

- [ ] **Step 2: Verify TypeScript compiles**

```bash
cd /Users/roger/Documents/docker-demo/frontend && npx tsc --noEmit 2>&1
```

Expected: no errors

- [ ] **Step 3: Commit**

```bash
cd /Users/roger/Documents/docker-demo
git add frontend/src/pages/BriefPage.tsx
git commit -m "feat(ui): BriefPage — standalone bride-facing brief"
```

---

## Task 5: App.tsx routing + ProfileScreen "Copiar link" button

**Files:**
- Modify: `frontend/src/App.tsx`
- Modify: `frontend/src/screens/ProfileScreen.tsx`

- [ ] **Step 1: Add BriefPage route to App.tsx**

In `/Users/roger/Documents/docker-demo/frontend/src/App.tsx`, add the import after the existing imports:

```ts
import { BriefPage } from './pages/BriefPage';
```

Then, at the very top of the `App()` function body — before the `const mobile = useIsMobile();` line — add:

```ts
const pathname = window.location.pathname;
if (pathname.startsWith('/brief/')) {
  const token = pathname.replace('/brief/', '');
  return <BriefPage token={token} />;
}
```

- [ ] **Step 2: Add useEffect import to ProfileScreen.tsx**

In `/Users/roger/Documents/docker-demo/frontend/src/screens/ProfileScreen.tsx`, the current first line is:
```ts
import { useState } from 'react';
```

Replace with:
```ts
import { useState, useEffect } from 'react';
```

- [ ] **Step 3: Add briefToken state + useEffect to ProfileScreen.tsx**

In `/Users/roger/Documents/docker-demo/frontend/src/screens/ProfileScreen.tsx`, add two new state variables inside `ProfileScreen`. Place them after the existing `const [tab, setTab]` line:

```ts
const [briefToken, setBriefToken] = useState<string | null>(null);
const [copied, setCopied] = useState(false);
```

Then add a `useEffect` after those state lines (before `if (!c) return null;`):

```ts
useEffect(() => {
  api.getIntake(c.id)
    .then(data => setBriefToken(data?.token ?? null))
    .catch(() => setBriefToken(null));
}, [c.id]);
```

- [ ] **Step 3: Add handleCopyLink function to ProfileScreen.tsx**

After the `useEffect` from Step 2, add:

```ts
const handleCopyLink = async () => {
  if (!briefToken) return;
  await navigator.clipboard.writeText(`${window.location.origin}/brief/${briefToken}`);
  setCopied(true);
  setTimeout(() => setCopied(false), 2000);
};
```

- [ ] **Step 4: Update back bar in ProfileScreen.tsx**

Find the back bar div. It currently ends with:

```tsx
  <Label style={{ color: T.ink3 }}>02 · Fitxa</Label>
</div>
```

Replace that `<Label>` line with a flex group that contains both the button and the label:

```tsx
  <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
    {briefToken && (
      <button
        onClick={handleCopyLink}
        style={{
          background: 'none', border: 'none', cursor: 'pointer',
          fontFamily: T.mono, fontSize: 10, letterSpacing: 0.8,
          textTransform: 'uppercase', padding: 0,
          color: copied ? T.accent : T.ink3,
        }}
      >
        {copied ? 'Copiat ✓' : 'Copiar link'}
      </button>
    )}
    <Label style={{ color: T.ink3 }}>02 · Fitxa</Label>
  </div>
</div>
```

- [ ] **Step 5: Verify TypeScript compiles**

```bash
cd /Users/roger/Documents/docker-demo/frontend && npx tsc --noEmit 2>&1
```

Expected: no errors

- [ ] **Step 6: Manual smoke test**

Start backend and frontend:
```bash
# Terminal 1
cd /Users/roger/Documents/docker-demo/backend && uvicorn main:app --reload --port 8000
# Terminal 2
cd /Users/roger/Documents/docker-demo/frontend && npm run dev
```

Verify:
1. Open http://localhost:5173 — app loads normally (brief route not triggered)
2. Open http://localhost:5173/brief/tok_aina_a3f9k2 — BriefPage renders with Aina Puig's brief
3. Open http://localhost:5173/brief/invalid — renders "Aquest link no és vàlid."
4. Open a client profile — "Copiar link" button appears in the back bar
5. Click "Copiar link" — button changes to "Copiat ✓", then reverts

- [ ] **Step 7: Commit**

```bash
cd /Users/roger/Documents/docker-demo
git add frontend/src/App.tsx frontend/src/screens/ProfileScreen.tsx
git commit -m "feat(ui): brief route + Copiar link button in ProfileScreen"
```

---

## Task 6: Push to Railway

- [ ] **Step 1: Push**

```bash
cd /Users/roger/Documents/docker-demo && git push origin master
```

- [ ] **Step 2: Verify Railway deploy**

Once Railway redeploys, open the production URL and verify:
1. A client profile shows the "Copiar link" button
2. Clicking it copies a URL like `https://your-app.railway.app/brief/tok_aina_a3f9k2`
3. Opening that URL shows the bride-facing brief page
