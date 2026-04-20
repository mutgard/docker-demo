# Intake Tab — Design Spec
**Date:** 2026-04-20
**Status:** Approved

---

## Overview

Add an **Intake** tab to each client's `ProfileScreen`. It surfaces how the client first contacted Juliette Atelier — either a WhatsApp conversation thread or a website contact form submission — plus an extracted brief and any related documents.

This is **demo mode only**. All data is mocked via static JSON files. When real data is needed, only the backend endpoint changes; the frontend API contract is identical.

---

## Architecture

### Backend endpoint

```
GET /clients/{id}/intake
```

Reads `backend/data/intake/client_{id}.json` and returns it verbatim. Returns `404` if the file doesn't exist (client has no intake yet).

No model validation on the backend for now — the JSON is served as-is. When we switch to real data, the endpoint will call the WhatsApp MCP or query the web form database instead.

### JSON file structure

Every file has a top-level `source` field:

```jsonc
// WhatsApp source
{
  "source": "whatsapp",
  "thread": [
    { "role": "client" | "julia", "text": "...", "time": "DD MMM HH:MM" }
  ],
  "brief": { /* shared shape — see below */ },
  "documents": [ /* shared shape — see below */ ]
}

// Web form source
{
  "source": "web_form",
  "submitted_at": "YYYY-MM-DD",
  "form_data": {
    "name": "...",
    "email": "...",
    "phone": "...",
    "wedding_date": "...",
    "venue": "...",
    "style_notes": "...",
    "budget_range": "...",
    "how_did_you_hear": "..."
  },
  "brief": { /* shared shape */ },
  "documents": [ /* shared shape */ ]
}
```

### Shared `brief` shape

```jsonc
{
  "wedding_date": "17 Mai 2026",
  "venue": "...",
  "garment": "...",
  "style": "...",
  "budget_tier": "Standard | Premium | Couture",
  "fabric_notes": "...",
  "extra_notes": "..."
}
```

### Shared `documents` shape

```jsonc
[
  { "label": "Proposta inicial", "type": "pdf", "url": "/static/docs/..." }
]
```

For demo mode, `url` is `null` and the frontend shows a disabled "Pendent" state instead of a link.

---

## Frontend UI

### Placement

`ProfileScreen` currently has no tabs — it's a single scrollable view. We introduce a minimal tab strip below the hero section with two tabs:

- **"Fitxa"** — the existing profile content (appointments, payments, fabrics)
- **"Ingrés"** — the new intake view

Tab strip uses the same mono/serif language as the rest of the app. Active tab has a bottom border in `T.accent`.

### Desktop layout (≥768px)

Two-column split inside the tab panel:
- **Left (60%)**: Thread or form submission view (scrollable)
- **Right (40%)**: Brief panel + Documents section (fixed height, scrollable internally)

### Mobile layout (<768px)

Single column, stacked:
1. Thread / form view
2. Brief panel
3. Documents

### WhatsApp thread view

Chat bubbles:
- Client messages: left-aligned, light background (`T.sheet` / `T.hairline`), mono timestamp below
- Julia's messages: right-aligned, accent color background (`T.accent`), white text, mono timestamp below
- Header shows "WhatsApp · {client phone}" in mono small caps

### Web form view

"Receipt" card showing:
- Header: "Formulari web · {submitted_at}" with a small badge `via web`
- Fields rendered as labeled rows: `LABEL ···· value` (mono label, serif value)
- Same visual language as the brief panel

### Brief panel

Labeled rows using existing app primitives:
- `<Label>` for field names (mono, uppercase, ink3)
- `<Serif>` for values
- Thin `<Rule>` between each row

### Documents section

Below the brief. Each document: PDF icon + `<Mono>` label + small "Obrir" link. For demo, links open the placeholder PDF.

---

## Mock content — client assignments

| # | Client | Source | Personality |
|---|--------|--------|-------------|
| 1 | Aina Puig | WhatsApp | Knows exactly what she wants — V-neck, needs to dance |
| 2 | Berta Soler | Web form | New lead, filled the form after seeing Instagram |
| 3 | Clara Ferrer | WhatsApp | Very specific, royal/structured, many references |
| 4 | Dolors Vidal | WhatsApp | Unsure, brings Pinterest boards, exploring |
| 5 | Elena Roca | WhatsApp | Relaxed, boho, trusts Julia's taste |
| 6 | Fina Batlle | Web form | Already delivered; initial intake was via website |

Each WhatsApp thread: 8–12 messages. Each web form: all fields filled with realistic Catalan bridal context.

---

## API client addition

Add `getIntake(clientId: number)` to `src/api.ts`:

```ts
getIntake: (id: number) => fetch(`${BASE}/clients/${id}/intake`).then(r => r.ok ? r.json() : null)
```

Returns `null` if 404 (no intake data yet) — frontend shows an empty state.

---

## Out of scope

- Real WhatsApp MCP integration (future switch)
- Editing or replying to intake data
- Multiple intake sessions per client
- PDF generation from brief
