# Client Brief (Shareable) — Design Spec
**Date:** 2026-04-20
**Status:** Approved

---

## Overview

Each client gets a shareable brief link Julia can copy and send to the bride. The bride opens the URL on her own device and sees a beautiful, standalone page with her dress proposal — no app login, no internal data exposed.

---

## Architecture

### Token storage

Each intake JSON file (`backend/data/intake/client_{id}.json`) gets a new top-level `token` field:

```json
{ "token": "tok_aina_a3f9k2", ... }
```

Tokens are short, opaque, unguessable strings. They are static in demo mode.

### Backend endpoint

New file `backend/routes/brief.py`:

```
GET /brief/:token
```

- Scans all intake files under `backend/data/intake/`
- Finds the file whose `token` matches
- Returns only bride-safe fields (see below) — budget tier, extra_notes, and source data are never sent
- Returns `404` if no match

**Response shape:**
```json
{
  "client_name": "Aina Puig",
  "wedding_date": "17 Mai 2026",
  "venue": "Masia, cerimònia a l'aire lliure",
  "garment": "Vestit a mida · Princesa modern",
  "style": "Escot en V profund, sense mànigues, puntilla Chantilly a l'escot, faldilla amb volum",
  "fabric_notes": "Mikado seda marfil (cos), tul francès (vel), puntilla Chantilly (vora)"
}
```

The backend reads `client_name` from a `client_name` field added directly to each intake JSON (alongside `token`). No database lookup needed.

### Frontend route

New standalone page at `/brief/:token`:
- Rendered by a new component `frontend/src/pages/BriefPage.tsx`
- Fetches `GET /brief/:token` from the backend
- No app shell (no Sidebar, no MobileHeader, no navigation)
- Full-page layout, works on mobile and desktop

### TypeScript type

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

### API client method

```ts
getBrief: async (token: string): Promise<ClientBrief | null> => {
  const r = await fetch(`${BASE}/brief/${token}`);
  if (r.status === 404) return null;
  if (!r.ok) throw new Error(`GET /brief/${token} → ${r.status}`);
  return r.json();
}
```

### Route handling (no React Router)

The app uses state-based navigation with no router library. Handle the brief route at the top of `App.tsx`:

```tsx
// At the very top of the App() function body, before any other logic:
const pathname = window.location.pathname;
if (pathname.startsWith('/brief/')) {
  const token = pathname.replace('/brief/', '');
  return <BriefPage token={token} />;
}
```

This short-circuits before any app shell rendering. `BriefPage` receives the token as a prop.

---

## Bride-Facing Page (`BriefPage`)

Standalone full-screen page — no app chrome.

**Structure (top to bottom):**

1. **Atelier header** — centered, with top padding
   - `Juliette` in serif (normal weight) + `Atelier` in serif italic, gold color
   - Thin hairline rule below

2. **Hero** — client name in large italic serif (40–48px), centered
   - Below: `Proposta · {wedding_date}` in small mono

3. **Brief rows** — four labeled sections, generous spacing:
   - `LLOC` → venue value
   - `PEÇA` → garment value
   - `ESTIL` → style value (largest field, wraps naturally)
   - `TELES` → fabric_notes value

4. **Footer** — centered, bottom of page
   - `Juliette Atelier` in small mono, `T.ink3` color

**Invalid/not-found state:** Centered message "Aquest link no és vàlid." — no other information.

**Loading state:** Blank page with subtle spinner or just blank until loaded.

**Responsive:** Works on mobile. Max-width ~680px, centered on desktop.

---

## "Copiar link" Button

Located in the back bar of `ProfileScreen` (top row, right side — next to the "02 · Fitxa" label).

**Behavior:**
1. On click: calls `api.getIntake(client.id)` to get the token
2. Constructs URL: `window.location.origin + '/brief/' + token`
3. Copies via `navigator.clipboard.writeText()`
4. Button label changes to "Copiat ✓" for 2 seconds, then reverts to "Copiar link"
5. If intake returns `null` (no token): button is hidden entirely

**Placement:** Rendered in the back bar div, alongside the existing "02 · Fitxa" label. Styled as a small mono text button (no border, subtle).

---

## Intake JSON updates

Add two new fields to each of the 6 intake JSON files:

| Client | token | client_name |
|--------|-------|-------------|
| client_1.json (Aina) | `tok_aina_a3f9k2` | `Aina Puig` |
| client_2.json (Berta) | `tok_berta_m7p4n8` | `Berta Soler` |
| client_3.json (Clara) | `tok_clara_z2x8v5` | `Clara Ferrer` |
| client_4.json (Dolors) | `tok_dolors_k9q1w3` | `Dolors Vidal` |
| client_5.json (Elena) | `tok_elena_r6t0j7` | `Elena Roca` |
| client_6.json (Fina) | `tok_fina_b4y2s9` | `Fina Batlle` |

---

## CORS / Router ordering

The `/brief/:token` frontend route must be registered **before** the static file mount in `main.py` so Railway's backend doesn't intercept it. Since the brief endpoint is an API route (`/brief/...`) and the static mount handles everything else, this works by default — no change needed.

The backend `brief` router uses prefix `/brief` (not `/clients`) to avoid overlap.

---

## Out of scope

- Authentication or expiry of brief links
- Editing the brief from the bride-facing page
- Sending the link via email/WhatsApp directly from the app
- PDF export
