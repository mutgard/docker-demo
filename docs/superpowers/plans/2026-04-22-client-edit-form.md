# Client Edit Form Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add inline editing to ProfileScreen so Julia can update client name, contact, garment, and notes without leaving the profile view.

**Architecture:** Toggle an `editing` boolean in ProfileScreen. When true, text fields become `<input>` / `<textarea>` / `<select>` elements in-place. On save, call the existing `PATCH /clients/{id}` endpoint (already wired in `api.patchClient`). On cancel, revert to original values. No new files, no backend changes.

**Tech Stack:** React + TypeScript inline styles, existing `T` token system, existing `api.patchClient` method.

---

## File Map

**Modified only:**
- `frontend/src/screens/ProfileScreen.tsx:20-239` — add `editing` state, `editFields` draft state, edit/save/cancel handlers, conditional field rendering

---

## Task 1: Edit state and draft fields

**Files:**
- Modify: `frontend/src/screens/ProfileScreen.tsx`

- [ ] **Step 1.1: Add editing state and draft**

In the state block at the top of `ProfileScreen` (after `const [clientEvents, setClientEvents] = useState<AtelierEvent[]>([])`), add:

```tsx
const [editing, setEditing] = useState(false);
const [draft, setDraft] = useState({
  name: '',
  phone: '',
  email: '',
  wedding_date: '',
  wedding_date_iso: '',
  garment: '',
  garment_style: '',
  notes: '',
  status: '' as import('../types').ClientStatus,
});
```

- [ ] **Step 1.2: Add startEdit and cancelEdit handlers**

After the `handleToggle` function, add:

```tsx
const startEdit = () => {
  setDraft({
    name: c.name,
    phone: c.phone,
    email: c.email,
    wedding_date: c.wedding_date,
    wedding_date_iso: c.wedding_date_iso ?? '',
    garment: c.garment,
    garment_style: c.garment_style,
    notes: c.notes,
    status: c.status,
  });
  setEditing(true);
};

const cancelEdit = () => setEditing(false);
```

- [ ] **Step 1.3: Add saveEdit handler**

After `cancelEdit`, add:

```tsx
const saveEdit = async () => {
  const days = draft.wedding_date_iso
    ? Math.round((new Date(draft.wedding_date_iso).getTime() - Date.now()) / 86400000)
    : c.days_until;
  const wedding_date = draft.wedding_date_iso
    ? (() => { const [y, m, d] = draft.wedding_date_iso.split('-'); return `${d}.${m}.${y}`; })()
    : c.wedding_date;
  await api.patchClient(c.id, {
    name: draft.name,
    phone: draft.phone,
    email: draft.email,
    wedding_date,
    wedding_date_iso: draft.wedding_date_iso || undefined,
    days_until: days,
    garment: draft.garment,
    garment_style: draft.garment_style,
    notes: draft.notes,
    status: draft.status,
  });
  const updated = await api.getClient(c.id);
  setC(updated);
  onRefresh();
  setEditing(false);
};
```

- [ ] **Step 1.4: Commit**

```bash
git add frontend/src/screens/ProfileScreen.tsx
git commit -m "feat(profile): add editing state + draft + save/cancel handlers"
```

---

## Task 2: Edit / Save / Cancel buttons in the back bar

**Files:**
- Modify: `frontend/src/screens/ProfileScreen.tsx` — the back bar `<div>` (lines ~69–89)

- [ ] **Step 2.1: Replace the right side of the back bar**

Replace the `<div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>` block inside the back bar with:

```tsx
<div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
  {!editing && briefToken && (
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
  {!editing && (
    <button
      onClick={startEdit}
      style={{
        background: 'none', border: 'none', cursor: 'pointer',
        fontFamily: T.mono, fontSize: 10, letterSpacing: 0.8,
        textTransform: 'uppercase', padding: 0, color: T.ink3,
      }}
    >
      Editar
    </button>
  )}
  {editing && (
    <>
      <button
        onClick={cancelEdit}
        style={{
          background: 'none', border: 'none', cursor: 'pointer',
          fontFamily: T.mono, fontSize: 10, letterSpacing: 0.8,
          textTransform: 'uppercase', padding: 0, color: T.ink3,
        }}
      >
        Cancel·lar
      </button>
      <button
        onClick={saveEdit}
        style={{
          background: 'none', border: 'none', cursor: 'pointer',
          fontFamily: T.mono, fontSize: 10, letterSpacing: 0.8,
          textTransform: 'uppercase', padding: 0, color: T.accent,
        }}
      >
        Guardar
      </button>
    </>
  )}
  <Label style={{ color: T.ink3 }}>02 · Fitxa</Label>
</div>
```

- [ ] **Step 2.2: Commit**

```bash
git add frontend/src/screens/ProfileScreen.tsx
git commit -m "feat(profile): edit/save/cancel buttons in back bar"
```

---

## Task 3: Editable hero section (name, status, phone, email)

**Files:**
- Modify: `frontend/src/screens/ProfileScreen.tsx` — the Hero `<div>` block (~line 92–111)

- [ ] **Step 3.1: Make hero fields conditional on `editing`**

The shared input style used in `NewClientScreen`:
```tsx
const fieldInput = {
  border: 'none',
  borderBottom: `1px solid ${T.hairline2}`,
  background: 'transparent',
  outline: 'none',
  padding: '4px 0',
  color: T.ink,
};
```

Add this constant near the top of the render body (before `return`), then replace the hero `<div style={{ flex: 1 }}>` contents with:

```tsx
<div style={{ flex: 1 }}>
  {editing ? (
    <input
      value={draft.name}
      onChange={e => setDraft(d => ({ ...d, name: e.target.value }))}
      style={{ ...fieldInput, fontFamily: T.serif, fontSize: mobile ? 28 : 36, fontStyle: 'italic', letterSpacing: -0.5, width: '100%' }}
    />
  ) : (
    <Serif size={mobile ? 32 : 40} italic>{c.name}</Serif>
  )}
  <div style={{ marginTop: 6, display: 'flex', gap: 8, flexWrap: 'wrap', alignItems: 'center' }}>
    {editing ? (
      <select
        value={draft.status}
        onChange={e => setDraft(d => ({ ...d, status: e.target.value as import('../types').ClientStatus }))}
        style={{
          appearance: 'none', WebkitAppearance: 'none',
          border: `1px solid ${T.hairline2}`,
          background: 'transparent', color: T.ink,
          fontFamily: T.mono, fontSize: 10, letterSpacing: 0.8,
          textTransform: 'uppercase', padding: '3px 10px',
          borderRadius: 999, cursor: 'pointer', outline: 'none',
        }}
      >
        {(['prospect', 'sense-paga', 'clienta', 'entregada'] as const).map(s => (
          <option key={s} value={s}>{s}</option>
        ))}
      </select>
    ) : (
      <Badge status={c.status} />
    )}
    {!editing && clientEvents.length > 0 && (
      <Mono size={10} color={T.ink3}>
        {clientEvents[0].title} · {clientEvents[0].date}
      </Mono>
    )}
  </div>
  {editing ? (
    <div style={{ marginTop: 8, display: 'flex', flexDirection: 'column', gap: 6 }}>
      <input value={draft.phone} onChange={e => setDraft(d => ({ ...d, phone: e.target.value }))}
        placeholder="Telèfon" style={{ ...fieldInput, fontFamily: T.mono, fontSize: 12, color: T.ink2 }} />
      <input value={draft.email} onChange={e => setDraft(d => ({ ...d, email: e.target.value }))}
        placeholder="Email" type="email" style={{ ...fieldInput, fontFamily: T.mono, fontSize: 12, color: T.ink2 }} />
    </div>
  ) : (
    (c.phone || c.email) && (
      <div style={{ marginTop: 8, display: 'flex', gap: 16, flexWrap: 'wrap' }}>
        {c.phone && <Mono size={10} color={T.ink2}>{c.phone}</Mono>}
        {c.email && <Mono size={10} color={T.ink2}>{c.email}</Mono>}
      </div>
    )
  )}
</div>
```

- [ ] **Step 3.2: Commit**

```bash
git add frontend/src/screens/ProfileScreen.tsx
git commit -m "feat(profile): editable hero — name, status, phone, email"
```

---

## Task 4: Editable Boda date and Peça section

**Files:**
- Modify: `frontend/src/screens/ProfileScreen.tsx` — countdown card + Peça section

- [ ] **Step 4.1: Add wedding date edit above countdown card**

Replace the countdown card block with:

```tsx
{editing && (
  <div style={{ marginBottom: 16 }}>
    <Label style={{ marginBottom: 8 }}>Data de boda</Label>
    <input
      type="date"
      value={draft.wedding_date_iso}
      onChange={e => setDraft(d => ({ ...d, wedding_date_iso: e.target.value }))}
      style={{ ...fieldInput, fontFamily: T.mono, fontSize: 13, color: T.ink, padding: '6px 0', width: '100%' }}
    />
  </div>
)}
{!editing && c.status !== 'entregada' && (
  /* existing countdown card unchanged */
  <div style={{ background: T.ink, color: T.paper, padding: '18px 22px', marginBottom: 24 }}>
    ...
  </div>
)}
```

Note: keep the existing countdown card block exactly as-is, just wrap it in `{!editing && c.status !== 'entregada' && (...)}`

- [ ] **Step 4.2: Make Peça fields editable**

Replace the Peça section's inner rows with:

```tsx
<div style={{ marginBottom: 24 }}>
  <Label style={{ marginBottom: 10 }}>Peça</Label>
  <div style={{ display: 'flex', flexDirection: 'column', gap: 0 }}>
    {([
      ['Tipus', 'garment', c.garment],
      ['Estil', 'garment_style', c.garment_style],
    ] as [string, 'garment' | 'garment_style', string][]).map(([label, key, val]) => (
      <div key={key} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '7px 0', borderBottom: `1px solid ${T.hairline}` }}>
        <Mono size={10} color={T.ink3}>{label}</Mono>
        {editing ? (
          <input
            value={draft[key]}
            onChange={e => setDraft(d => ({ ...d, [key]: e.target.value }))}
            placeholder="—"
            style={{ border: 'none', background: 'transparent', outline: 'none', fontFamily: T.mono, fontSize: 10, color: T.ink, textAlign: 'right', width: '60%' }}
          />
        ) : (
          val ? <Mono size={10} color={T.ink}>{val}</Mono> : null
        )}
      </div>
    ))}
    {!editing && c.measurements_date && (
      <div style={{ display: 'flex', justifyContent: 'space-between', padding: '7px 0', borderBottom: `1px solid ${T.hairline}` }}>
        <Mono size={10} color={T.ink3}>Data mides</Mono>
        <Mono size={10} color={T.ink}>{c.measurements_date}</Mono>
      </div>
    )}
  </div>
</div>
```

- [ ] **Step 4.3: Commit**

```bash
git add frontend/src/screens/ProfileScreen.tsx
git commit -m "feat(profile): editable wedding date + garment fields"
```

---

## Task 5: Editable Notes

**Files:**
- Modify: `frontend/src/screens/ProfileScreen.tsx` — Notes section at bottom

- [ ] **Step 5.1: Replace Notes section**

Replace the notes block (currently `{c.notes && (...)}`) with:

```tsx
{(editing || c.notes) && (
  <div style={{ marginBottom: 24 }}>
    <Label style={{ marginBottom: 8 }}>Notes</Label>
    {editing ? (
      <textarea
        value={draft.notes}
        onChange={e => setDraft(d => ({ ...d, notes: e.target.value }))}
        placeholder="Notes sobre la clienta…"
        rows={4}
        style={{
          width: '100%', border: `1px solid ${T.hairline}`, background: 'transparent',
          outline: 'none', fontFamily: T.sans, fontSize: 13, color: T.ink,
          lineHeight: 1.65, padding: '8px', resize: 'vertical', boxSizing: 'border-box' as const,
        }}
      />
    ) : (
      <div style={{ fontFamily: T.sans, fontSize: 13, color: T.ink2, lineHeight: 1.65 }}>{c.notes}</div>
    )}
  </div>
)}
```

- [ ] **Step 5.2: Verify full edit flow manually**

```bash
cd frontend && npm run dev
```

1. Open a client profile
2. Click "Editar" in the top bar
3. Edit name, phone, garment, notes
4. Click "Guardar" → verify changes persist after refresh
5. Edit again, click "Cancel·lar" → verify values revert

- [ ] **Step 5.3: Verify backend test still passes**

```bash
cd backend && python -m pytest tests/test_clients.py::test_patch_client_status -v
```

Expected: PASS

- [ ] **Step 5.4: Final commit**

```bash
git add frontend/src/screens/ProfileScreen.tsx
git commit -m "feat(profile): editable notes — complete inline edit form"
```

---

## Self-Review

**Spec coverage:**
- Edit name, wedding date, phone, email, garment, garment_style, notes, status ✓
- Inline in ProfileScreen (no new screen) ✓
- Save calls PATCH /clients/{id} ✓
- Cancel reverts without API call ✓
- No new files ✓

**Type consistency:** `draft.status` typed as `ClientStatus` via import ✓. `api.patchClient` accepts `Partial<Client>` ✓.
