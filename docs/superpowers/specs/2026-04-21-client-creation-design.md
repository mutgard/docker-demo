# Client Creation — Design Spec
_2026-04-21_

## Overview

From the Clients screen a `+` button opens a creation form. On mobile it pushes as a full screen; on desktop it appears as a modal overlay. The form mirrors `ProfileScreen`'s visual structure with editable fields. Name and wedding date are required; all other fields are optional. Status defaults to `prospect` but is selectable. On success the app navigates directly to the new client's profile.

---

## Entry point

- A `+` button is added to `ClientsScreen`'s header area (desktop: top-right of `PageHeader`; mobile: same area as the search row).
- `ClientsScreen` receives an `onCreate: () => void` prop wired to this button.
- `App.tsx` adds `creating: boolean` state (default `false`). `onCreate` sets it to `true`.

**Mobile:** `Screen` type gains `'create'`. `screen === 'create'` renders `NewClientScreen` full-screen within the existing mobile shell.

**Desktop:** When `creating === true`, a modal overlay renders on top of the clients list — fixed fullscreen semi-transparent backdrop + a centered `480px`-wide scrollable panel using existing `T.*` tokens.

---

## `NewClientScreen` layout

Matches `ProfileScreen`'s structure section by section. Responsive padding: `mobile ? 20 : 40`px.

### Nav bar
- Left: "← Clientes" cancel button (clears `creating` / returns to `clients` screen).
- Right: `T.mono` uppercase label "Nova clienta".

### Hero section
Same dark/paper background as `ProfileScreen` hero. Contains:
- **Avatar** — circle showing live initials from name input; falls back to `?` when empty.
- **Name input** — styled as `Serif` italic, large (matches `ProfileScreen`'s name display). Required. Red border on submit if empty.
- **Status select** — `<select>` styled as a `Badge`-like element (`T.mono` uppercase, pill border). Options: `prospect`, `sense-paga`, `clienta`, `entregada`. Default: `prospect`. Positioned where `<Badge>` sits in `ProfileScreen`.
- **Phone input** — `Mono size 10`, optional.
- **Email input** — `Mono size 10`, optional.

### Boda section
- `<input type="date">` for wedding date. Required. Red border on submit if empty.
- `days_until` is not shown — computed on submit.

### Peça section
- Tipus (`garment`) — text input, KV-row style.
- Estil (`garment_style`) — text input, KV-row style.

### Notes section
- `<textarea>` styled with `T.sans` font, same color as `ProfileScreen` notes display.

### Submit button
- Full-width at bottom: "Crear clienta".
- Disabled while request is in flight.
- Inline error message below if POST fails: "Error en crear la clienta. Torna-ho a provar."

---

## Data flow

1. User submits → validate name (non-empty) and wedding_date (non-empty). Highlight invalid fields with red border; do not submit.
2. Compute `days_until = Math.round((new Date(weddingDateISO) - new Date()) / 86400000)`.
3. Format display string: `wedding_date = DD.MM.YYYY` from ISO input value.
4. Call `api.createClient({ name, wedding_date, days_until, status, phone, email, garment, garment_style, notes })`.
5. On success: call `refresh()` to reload clients list, then `openClient(newClient.id)` to navigate to the new profile.
6. On error: show inline error, re-enable submit button.

### `api.ts` changes
- Add `post<T>(path, body)` helper alongside existing `get` and `patch`.
- Add `createClient: (body: ClientCreate) => post<Client>('/clients', body)`.

### `types.ts` changes
- Add `ClientCreate` interface: `{ name: string; wedding_date: string; days_until: number; status: ClientStatus; garment?: string; garment_style?: string; measurements_date?: string; phone?: string; email?: string; notes?: string; }`.

---

## Files touched

| File | Change |
|------|--------|
| `frontend/src/App.tsx` | Add `creating` state, `Screen` type update, wire `onCreate`/cancel, render `NewClientScreen` (modal or screen) |
| `frontend/src/screens/ClientsScreen.tsx` | Add `onCreate` prop, `+` button in header |
| `frontend/src/screens/NewClientScreen.tsx` | New file — creation form |
| `frontend/src/api.ts` | Add `post` helper + `createClient` method |
| `frontend/src/types.ts` | Add `ClientCreate` interface |

No backend changes required — `POST /clients` already exists and accepts all fields.

---

## Out of scope
- Fabrics, appointments, payments at creation — added later from the profile.
- Edit mode for existing clients.
- Inline date formatting feedback while typing.
