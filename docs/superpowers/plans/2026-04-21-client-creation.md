# Client Creation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a `+` button to the Clients screen that opens a creation form — modal on desktop, full screen on mobile — allowing Julia to create a new client record with name (required), wedding date (required), status (default prospect), phone, email, garment, and notes.

**Architecture:** A new `NewClientScreen` component mirrors `ProfileScreen`'s visual structure with editable inputs. `App.tsx` manages a `creating` boolean; on mobile this replaces the content area, on desktop it renders as a fixed modal overlay. No backend changes needed — `POST /clients` already exists.

**Tech Stack:** React 18, TypeScript, inline styles with `T.*` tokens, Vite, FastAPI backend (no changes needed).

---

## File Map

| File | Action | Responsibility |
|------|--------|----------------|
| `frontend/src/types.ts` | Modify | Add `ClientCreate` interface |
| `frontend/src/api.ts` | Modify | Add `post` helper + `createClient` method |
| `frontend/src/screens/NewClientScreen.tsx` | Create | Creation form — all inputs, validation, submit |
| `frontend/src/screens/ClientsScreen.tsx` | Modify | Add `onCreate` prop + `+` button in header |
| `frontend/src/App.tsx` | Modify | Add `creating` state, wire `onCreate`/cancel, render modal or screen |

---

## Task 1: Add `ClientCreate` type and `createClient` API method

**Files:**
- Modify: `frontend/src/types.ts`
- Modify: `frontend/src/api.ts`

- [ ] **Step 1: Add `ClientCreate` to `types.ts`**

Open `frontend/src/types.ts`. After the `Client` interface, add:

```typescript
export interface ClientCreate {
  name: string;
  wedding_date: string;
  days_until: number;
  status: ClientStatus;
  garment?: string;
  garment_style?: string;
  measurements_date?: string;
  phone?: string;
  email?: string;
  notes?: string;
}
```

- [ ] **Step 2: Add `post` helper and `createClient` to `api.ts`**

Open `frontend/src/api.ts`. Add the `post` helper after the `patch` helper, then add `createClient` to the `api` object:

```typescript
async function post<T>(path: string, body: unknown): Promise<T> {
  const r = await fetch(`${BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!r.ok) throw new Error(`POST ${path} → ${r.status}`);
  return r.json();
}
```

In the `api` export object, add:
```typescript
createClient: (body: ClientCreate) => post<Client>('/clients', body),
```

Also update the import line at the top of `api.ts` to include `ClientCreate`:
```typescript
import type { Client, Fabric, ShoppingItem, ClientCreate } from './types';
```

- [ ] **Step 3: Verify TypeScript compiles**

```bash
cd /Users/roger/Documents/docker-demo/frontend && npx tsc --noEmit
```

Expected: no errors.

- [ ] **Step 4: Commit**

```bash
cd /Users/roger/Documents/docker-demo
git add frontend/src/types.ts frontend/src/api.ts
git commit -m "feat(types+api): ClientCreate type + createClient POST method"
```

---

## Task 2: Build `NewClientScreen`

**Files:**
- Create: `frontend/src/screens/NewClientScreen.tsx`

- [ ] **Step 1: Create the file with helpers and state**

Create `frontend/src/screens/NewClientScreen.tsx`:

```typescript
import { useState } from 'react';
import type { ClientStatus } from '../types';
import { api } from '../api';
import { T } from '../tokens';
import { Label, Mono } from '../components/primitives';
import { useIsMobile } from '../hooks/useIsMobile';
import { initials } from '../lib/clientHelpers';

interface Props {
  onCancel: () => void;
  onSuccess: (clientId: number) => void;
}

const STATUS_OPTIONS: { value: ClientStatus; label: string }[] = [
  { value: 'prospect',   label: 'Prospect' },
  { value: 'sense-paga', label: 'Sense paga' },
  { value: 'clienta',    label: 'Clienta' },
  { value: 'entregada',  label: 'Entregada' },
];

function computeDaysUntil(iso: string): number {
  return Math.round((new Date(iso).getTime() - Date.now()) / 86400000);
}

function formatWeddingDate(iso: string): string {
  const [y, m, d] = iso.split('-');
  return `${d}.${m}.${y}`;
}

export function NewClientScreen({ onCancel, onSuccess }: Props) {
  const mobile = useIsMobile();
  const [name, setName] = useState('');
  const [phone, setPhone] = useState('');
  const [email, setEmail] = useState('');
  const [weddingDateISO, setWeddingDateISO] = useState('');
  const [status, setStatus] = useState<ClientStatus>('prospect');
  const [garment, setGarment] = useState('');
  const [garmentStyle, setGarmentStyle] = useState('');
  const [notes, setNotes] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [nameError, setNameError] = useState(false);
  const [dateError, setDateError] = useState(false);

  const px = mobile ? 20 : 40;
  const s = T.badge[status];

  const fieldInput = (hasError = false): React.CSSProperties => ({
    border: 'none',
    borderBottom: `1px solid ${hasError ? T.accent : T.hairline2}`,
    background: 'transparent',
    outline: 'none',
    width: '100%',
    padding: '4px 0',
    color: T.ink,
  });

  const handleSubmit = async () => {
    const nErr = !name.trim();
    const dErr = !weddingDateISO;
    setNameError(nErr);
    setDateError(dErr);
    if (nErr || dErr) return;

    setSubmitting(true);
    setError('');
    try {
      const newClient = await api.createClient({
        name: name.trim(),
        phone,
        email,
        wedding_date: formatWeddingDate(weddingDateISO),
        days_until: computeDaysUntil(weddingDateISO),
        status,
        garment,
        garment_style: garmentStyle,
        notes,
      });
      onSuccess(newClient.id);
    } catch {
      setError('Error en crear la clienta. Torna-ho a provar.');
      setSubmitting(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', flex: '1 1 auto', minHeight: 0, overflow: 'hidden', background: T.paper }}>

      {/* Nav bar */}
      <div style={{ padding: `10px ${px}px`, borderBottom: `1px solid ${T.hairline}`, flexShrink: 0, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <button onClick={onCancel} style={{ background: 'none', border: 'none', cursor: 'pointer', fontFamily: T.mono, fontSize: 10, letterSpacing: 0.8, textTransform: 'uppercase', color: T.ink2, padding: 0 }}>
          ← Cancel·lar
        </button>
        <Label style={{ color: T.ink3 }}>Nova clienta</Label>
      </div>

      {/* Scrollable body */}
      <div style={{ flex: 1, overflow: 'auto', padding: `${mobile ? 20 : 28}px ${px}px 40px` }}>

        {/* Hero: avatar + name + status + contact */}
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: 20, marginBottom: 28 }}>
          <div style={{
            width: mobile ? 52 : 68, height: mobile ? 52 : 68, borderRadius: '50%',
            background: T.paper3, border: `1px solid ${T.hairline}`, flexShrink: 0,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontFamily: T.serif, fontStyle: 'italic', fontSize: mobile ? 20 : 26, color: T.ink2,
          }}>
            {name.trim() ? initials(name) : '?'}
          </div>
          <div style={{ flex: 1, minWidth: 0 }}>
            <input
              value={name}
              onChange={e => { setName(e.target.value); if (e.target.value.trim()) setNameError(false); }}
              placeholder="Nom de la clienta"
              style={{ ...fieldInput(nameError), fontFamily: T.serif, fontSize: mobile ? 28 : 36, fontStyle: 'italic', letterSpacing: -0.5 }}
            />
            {nameError && <Mono size={9} color={T.accent} style={{ marginTop: 4, display: 'block' }}>El nom és obligatori</Mono>}

            <div style={{ marginTop: 12 }}>
              <select
                value={status}
                onChange={e => setStatus(e.target.value as ClientStatus)}
                style={{
                  appearance: 'none', WebkitAppearance: 'none',
                  border: `1px ${s.dash ? 'dashed' : 'solid'} ${s.bd}`,
                  background: s.bg, color: s.fg,
                  fontFamily: T.mono, fontSize: 10, letterSpacing: 0.8,
                  textTransform: 'uppercase', padding: '3px 24px 3px 10px',
                  borderRadius: 999, cursor: 'pointer', outline: 'none',
                }}
              >
                {STATUS_OPTIONS.map(o => (
                  <option key={o.value} value={o.value}>{o.label}</option>
                ))}
              </select>
            </div>

            <div style={{ marginTop: 12, display: 'flex', flexDirection: 'column', gap: 8 }}>
              <input value={phone} onChange={e => setPhone(e.target.value)} placeholder="Telèfon"
                style={{ ...fieldInput(), fontFamily: T.mono, fontSize: 12, color: T.ink2 }} />
              <input value={email} onChange={e => setEmail(e.target.value)} placeholder="Email" type="email"
                style={{ ...fieldInput(), fontFamily: T.mono, fontSize: 12, color: T.ink2 }} />
            </div>
          </div>
        </div>

        {/* Boda */}
        <div style={{ marginBottom: 24 }}>
          <Label style={{ marginBottom: 10 }}>Boda</Label>
          <input
            type="date"
            value={weddingDateISO}
            onChange={e => { setWeddingDateISO(e.target.value); if (e.target.value) setDateError(false); }}
            style={{ ...fieldInput(dateError), fontFamily: T.mono, fontSize: 13, color: T.ink, padding: '6px 0' }}
          />
          {dateError && <Mono size={9} color={T.accent} style={{ marginTop: 4, display: 'block' }}>La data de boda és obligatòria</Mono>}
        </div>

        {/* Peça */}
        <div style={{ marginBottom: 24 }}>
          <Label style={{ marginBottom: 10 }}>Peça</Label>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 0 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '7px 0', borderBottom: `1px solid ${T.hairline}` }}>
              <Mono size={10} color={T.ink3}>Tipus</Mono>
              <input value={garment} onChange={e => setGarment(e.target.value)} placeholder="—"
                style={{ border: 'none', background: 'transparent', outline: 'none', fontFamily: T.mono, fontSize: 10, color: T.ink, textAlign: 'right', width: '60%' }} />
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '7px 0', borderBottom: `1px solid ${T.hairline}` }}>
              <Mono size={10} color={T.ink3}>Estil</Mono>
              <input value={garmentStyle} onChange={e => setGarmentStyle(e.target.value)} placeholder="—"
                style={{ border: 'none', background: 'transparent', outline: 'none', fontFamily: T.mono, fontSize: 10, color: T.ink, textAlign: 'right', width: '60%' }} />
            </div>
          </div>
        </div>

        {/* Notes */}
        <div style={{ marginBottom: 32 }}>
          <Label style={{ marginBottom: 10 }}>Notes</Label>
          <textarea
            value={notes}
            onChange={e => setNotes(e.target.value)}
            placeholder="Notes sobre la clienta…"
            rows={4}
            style={{
              width: '100%', border: `1px solid ${T.hairline}`, background: 'transparent',
              outline: 'none', fontFamily: T.sans, fontSize: 13, color: T.ink,
              lineHeight: 1.65, padding: '8px', resize: 'vertical', boxSizing: 'border-box',
            }}
          />
        </div>

        {error && (
          <Mono size={11} color={T.accent} style={{ marginBottom: 16, display: 'block' }}>{error}</Mono>
        )}

        <button
          onClick={handleSubmit}
          disabled={submitting}
          style={{
            width: '100%', padding: '14px',
            background: submitting ? T.ink3 : T.ink,
            color: T.paper, border: 'none',
            fontFamily: T.mono, fontSize: 12, letterSpacing: 0.8,
            textTransform: 'uppercase',
            cursor: submitting ? 'not-allowed' : 'pointer',
          }}
        >
          {submitting ? 'Creant…' : 'Crear clienta'}
        </button>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Verify TypeScript compiles**

```bash
cd /Users/roger/Documents/docker-demo/frontend && npx tsc --noEmit
```

Expected: no errors.

- [ ] **Step 3: Commit**

```bash
cd /Users/roger/Documents/docker-demo
git add frontend/src/screens/NewClientScreen.tsx
git commit -m "feat(ui): NewClientScreen — client creation form"
```

---

## Task 3: Add `+` button to `ClientsScreen`

**Files:**
- Modify: `frontend/src/screens/ClientsScreen.tsx`

- [ ] **Step 1: Add `onCreate` prop and `+` button**

Open `frontend/src/screens/ClientsScreen.tsx`.

Change the `Props` interface from:
```typescript
interface Props { clients: Client[]; onOpen: (id: number) => void; }
```
to:
```typescript
interface Props { clients: Client[]; onOpen: (id: number) => void; onCreate: () => void; }
```

Change the function signature from:
```typescript
export function ClientsScreen({ clients, onOpen }: Props) {
```
to:
```typescript
export function ClientsScreen({ clients, onOpen, onCreate }: Props) {
```

Define a `plusButton` element (before the `searchBox` definition):
```typescript
const plusButton = (
  <button
    onClick={onCreate}
    style={{
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      width: 34, height: 34, flexShrink: 0,
      border: `1px solid ${T.hairline2}`, background: T.vellum,
      cursor: 'pointer', borderRadius: 2,
    }}
    title="Nova clienta"
  >
    <svg width="14" height="14" viewBox="0 0 14 14" fill="none" stroke={T.ink2} strokeWidth="1.6" strokeLinecap="round">
      <path d="M7 1v12M1 7h12"/>
    </svg>
  </button>
);
```

**Desktop:** In the `PageHeader` `right` prop, add `plusButton` alongside `searchBox`:
```tsx
<PageHeader eyebrow="Atelier · Taller" title="Clientes" subtitle={`${clients.length} noives`}
  right={<>{searchBox}{plusButton}</>} />
```

**Mobile:** In the `PageHeader` `right` prop, add `plusButton` alongside `searchBox`:
```tsx
<PageHeader eyebrow="Atelier" title="Clientes" subtitle={`${clients.length}`}
  right={<>{searchBox}{plusButton}</>} />
```

- [ ] **Step 2: Verify TypeScript compiles**

```bash
cd /Users/roger/Documents/docker-demo/frontend && npx tsc --noEmit
```

Expected: no errors (will warn that `onCreate` is unused in `App.tsx` until next task — that's fine).

- [ ] **Step 3: Commit**

```bash
cd /Users/roger/Documents/docker-demo
git add frontend/src/screens/ClientsScreen.tsx
git commit -m "feat(ui): + button in ClientsScreen header"
```

---

## Task 4: Wire creation flow in `App.tsx`

**Files:**
- Modify: `frontend/src/App.tsx`

- [ ] **Step 1: Add `creating` state and `NewClientScreen` import**

Open `frontend/src/App.tsx`.

Add the import:
```typescript
import { NewClientScreen } from './screens/NewClientScreen';
```

Inside `AtelierApp`, add `creating` state after the existing state declarations:
```typescript
const [creating, setCreating] = useState(false);
```

- [ ] **Step 2: Add `handleCreateSuccess` handler**

Inside `AtelierApp`, add below the `refresh` constant:
```typescript
const handleCreateSuccess = (id: number) => {
  setCreating(false);
  refresh().then(() => openClient(id));
};
```

Note: `refresh` currently returns `void` — update it so we can chain `.then`:
```typescript
const refresh = () => api.listClients().then(setClients);
```
(It already returns the promise from `.then(setClients)` — just confirm it's not `void`-cast anywhere. It isn't — `useState`'s setter returns void but `api.listClients().then(setClients)` returns `Promise<void>`, which is fine.)

- [ ] **Step 3: Wire `onCreate` into `ClientsScreen` and add modal/screen rendering**

Replace the `content` block:
```tsx
const content = (
  <>
    {screen === 'clients' && !creating && <ClientsScreen clients={clients} onOpen={openClient} onCreate={() => setCreating(true)} />}
    {screen === 'clients' && creating && mobile && (
      <NewClientScreen onCancel={() => setCreating(false)} onSuccess={handleCreateSuccess} />
    )}
    {screen === 'profile' && clientId !== null && (
      <ProfileScreen
        client={clients.find(c => c.id === clientId) ?? clients[0]}
        onBack={back}
        onOpenFabrics={() => nav('fabrics')}
        onRefresh={refresh}
      />
    )}
    {screen === 'fabrics' && <FabricsScreen clients={clients} onRefresh={refresh} />}
    {screen === 'shop'    && <ShoppingScreen clients={clients} />}
  </>
);
```

Add the desktop modal just before the closing `</div>` of the desktop return (the `gridTemplateColumns` wrapper), after the `<Sidebar>` and content `<div>`:
```tsx
{creating && !mobile && (
  <div style={{
    position: 'fixed', inset: 0, zIndex: 100,
    background: 'rgba(42,31,20,0.45)',
    display: 'flex', alignItems: 'flex-start', justifyContent: 'center',
    padding: '48px 24px',
    overflowY: 'auto',
  }}>
    <div style={{
      width: 480, minHeight: 0,
      background: T.paper,
      boxShadow: '0 8px 48px rgba(0,0,0,0.28)',
      display: 'flex', flexDirection: 'column',
    }}>
      <NewClientScreen onCancel={() => setCreating(false)} onSuccess={handleCreateSuccess} />
    </div>
  </div>
)}
```

The full desktop return becomes:
```tsx
return (
  <div style={{ display: 'grid', gridTemplateColumns: '232px 1fr', width: '100%', height: '100%', background: T.paper, color: T.ink, fontFamily: T.sans }}>
    <Sidebar active={screen} onNav={nav} fabricsToBuy={fabricsToBuy} totalClients={clients.length} totalFabrics={totalFabrics} />
    <div style={{ minWidth: 0, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>{content}</div>
    {creating && !mobile && (
      <div style={{
        position: 'fixed', inset: 0, zIndex: 100,
        background: 'rgba(42,31,20,0.45)',
        display: 'flex', alignItems: 'flex-start', justifyContent: 'center',
        padding: '48px 24px',
        overflowY: 'auto',
      }}>
        <div style={{
          width: 480,
          maxHeight: 'calc(100vh - 96px)',
          background: T.paper,
          boxShadow: '0 8px 48px rgba(0,0,0,0.28)',
          display: 'flex', flexDirection: 'column',
        }}>
          <NewClientScreen onCancel={() => setCreating(false)} onSuccess={handleCreateSuccess} />
        </div>
      </div>
    )}
  </div>
);
```

- [ ] **Step 4: Verify TypeScript compiles**

```bash
cd /Users/roger/Documents/docker-demo/frontend && npx tsc --noEmit
```

Expected: no errors.

- [ ] **Step 5: Build the app**

```bash
cd /Users/roger/Documents/docker-demo/frontend && npm run build
```

Expected: build completes with no errors, outputs to `dist/`.

- [ ] **Step 6: Manual smoke test**

Start dev server:
```bash
cd /Users/roger/Documents/docker-demo/frontend && npm run dev
```

Verify:
1. Clients screen shows `+` button in the header.
2. Click `+` — desktop: modal appears over the client list; mobile: creation screen fills the view.
3. Clicking "← Cancel·lar" closes the form and returns to the client list.
4. Submit with empty name → red border + "El nom és obligatori" message appears.
5. Submit with name but no wedding date → red border + "La data de boda és obligatòria" appears.
6. Fill in name + wedding date, submit → spinner shows, on success navigates to the new profile.
7. New client appears in the clients list with status "Prospect".
8. Avatar in hero shows live initials as you type the name.
9. Status dropdown renders with badge styling and all four options.

- [ ] **Step 7: Commit**

```bash
cd /Users/roger/Documents/docker-demo
git add frontend/src/App.tsx
git commit -m "feat(ui): wire client creation — modal (desktop) + screen (mobile)"
```
