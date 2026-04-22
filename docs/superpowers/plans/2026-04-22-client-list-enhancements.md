# Client List Enhancements Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the client list more useful for Julia's daily workflow by adding sortable columns, urgency highlighting for imminent weddings, and a payment balance column.

**Note:** Search (by name) and status filter chips are already implemented in `ClientsScreen.tsx`. This plan adds the missing pieces on top.

**Architecture:** All changes are frontend-only in `ClientsScreen.tsx`. Sort state replaces the hardcoded `sort((a, b) => a.days_until - b.days_until)`. A `parsePayments` call per row adds the balance column. Urgency logic adds a colored left border to rows with ≤ 30 days to wedding. No new files, no backend changes.

**Tech Stack:** React + TypeScript, existing `T` token system, existing `parsePayments` helper from `clientHelpers.ts`.

---

## File Map

**Modified only:**
- `frontend/src/screens/ClientsScreen.tsx` — sort state, sort logic, urgency highlight, balance column

---

## Task 1: Sortable columns

**Files:**
- Modify: `frontend/src/screens/ClientsScreen.tsx`

- [ ] **Step 1.1: Add sort state**

At the top of `ClientsScreen`, after `const [search, setSearch] = useState('')`, add:

```tsx
type SortKey = 'days_until' | 'name' | 'status';
type SortDir = 'asc' | 'desc';
const [sortKey, setSortKey] = useState<SortKey>('days_until');
const [sortDir, setSortDir] = useState<SortDir>('asc');
```

- [ ] **Step 1.2: Add sort toggle handler**

After the sort state, add:

```tsx
const toggleSort = (key: SortKey) => {
  if (sortKey === key) {
    setSortDir(d => d === 'asc' ? 'desc' : 'asc');
  } else {
    setSortKey(key);
    setSortDir('asc');
  }
};
```

- [ ] **Step 1.3: Replace hardcoded sort in the `list` computation**

Replace `.sort((a, b) => a.days_until - b.days_until)` with:

```tsx
.sort((a, b) => {
  let cmp = 0;
  if (sortKey === 'days_until') cmp = a.days_until - b.days_until;
  if (sortKey === 'name') cmp = a.name.localeCompare(b.name);
  if (sortKey === 'status') {
    const order = ['prospect', 'sense-paga', 'clienta', 'entregada'];
    cmp = order.indexOf(a.status) - order.indexOf(b.status);
  }
  return sortDir === 'asc' ? cmp : -cmp;
})
```

- [ ] **Step 1.4: Add sort arrow helper**

Add after `toggleSort`:

```tsx
const sortArrow = (key: SortKey) => {
  if (sortKey !== key) return null;
  return <span style={{ marginLeft: 4, fontSize: 8 }}>{sortDir === 'asc' ? '▲' : '▼'}</span>;
};
```

- [ ] **Step 1.5: Make column headers clickable**

In the desktop table `<thead>`, replace the static header cells for Clienta, Estat, and Dies with clickable versions. Replace the `{['Clienta', 'Peça', 'Estat', 'Boda', 'Dies', 'Teles'].map(h => ...)}` block with:

```tsx
{([
  { label: 'Clienta', key: 'name' as SortKey },
  { label: 'Peça', key: null },
  { label: 'Estat', key: 'status' as SortKey },
  { label: 'Boda', key: null },
  { label: 'Dies', key: 'days_until' as SortKey },
  { label: 'Teles', key: null },
  { label: 'Pendent', key: null },
]).map(({ label, key }) => (
  <th key={label}
    onClick={key ? () => toggleSort(key) : undefined}
    style={{
      textAlign: 'left', padding: '8px 12px 8px 0',
      fontFamily: T.mono, fontSize: 9, letterSpacing: 1, textTransform: 'uppercase',
      color: key && sortKey === key ? T.ink2 : T.ink3,
      borderBottom: `1px solid ${T.hairline}`, fontWeight: 400,
      cursor: key ? 'pointer' : 'default',
      userSelect: 'none',
    }}
  >
    {label}{key && sortArrow(key)}
  </th>
))}
```

- [ ] **Step 1.6: Commit**

```bash
git add frontend/src/screens/ClientsScreen.tsx
git commit -m "feat(clients): sortable columns — name, status, days_until"
```

---

## Task 2: Urgency highlighting

**Files:**
- Modify: `frontend/src/screens/ClientsScreen.tsx`

- [ ] **Step 2.1: Add urgency helper**

After `const px = mobile ? 20 : 40;`, add:

```tsx
const urgency = (days: number, status: string): 'critical' | 'warning' | 'none' => {
  if (status === 'entregada') return 'none';
  if (days <= 14 && days >= 0) return 'critical';
  if (days <= 30 && days >= 0) return 'warning';
  return 'none';
};
```

- [ ] **Step 2.2: Apply urgency border to desktop table rows**

In the `<tr>` for each client row, update the style to include a left border based on urgency:

```tsx
<tr
  key={c.id}
  onClick={() => onOpen(c.id)}
  style={{
    cursor: 'pointer',
    borderBottom: `1px solid ${T.hairline}`,
    borderLeft: urgency(c.days_until, c.status) === 'critical'
      ? `3px solid ${T.accent}`
      : urgency(c.days_until, c.status) === 'warning'
      ? `3px solid ${T.gold}`
      : '3px solid transparent',
  }}
  onMouseEnter={e => { (e.currentTarget as HTMLElement).style.background = T.paper2; }}
  onMouseLeave={e => { (e.currentTarget as HTMLElement).style.background = 'transparent'; }}
>
```

- [ ] **Step 2.3: Apply urgency indicator to mobile cards**

In the mobile card `<div key={c.id} onClick=...>`, update the style:

```tsx
<div
  key={c.id}
  onClick={() => onOpen(c.id)}
  style={{
    background: T.vellum,
    border: `1px solid ${T.hairline}`,
    borderLeft: urgency(c.days_until, c.status) === 'critical'
      ? `3px solid ${T.accent}`
      : urgency(c.days_until, c.status) === 'warning'
      ? `3px solid ${T.gold}`
      : `1px solid ${T.hairline}`,
    borderRadius: 4,
    padding: '14px',
    marginBottom: 8,
    cursor: 'pointer',
  }}
>
```

- [ ] **Step 2.4: Commit**

```bash
git add frontend/src/screens/ClientsScreen.tsx
git commit -m "feat(clients): urgency highlighting — red ≤14 days, gold ≤30 days"
```

---

## Task 3: Outstanding balance column

**Files:**
- Modify: `frontend/src/screens/ClientsScreen.tsx`

- [ ] **Step 3.1: Add parsePayments import**

Add to the existing import from `clientHelpers`:
```tsx
import { initials, parsePayments } from '../lib/clientHelpers';
```

(Replace the current `import { initials } from '../lib/clientHelpers';`)

- [ ] **Step 3.2: Add balance cell to desktop table rows**

Inside the `<tr>` for each client in the desktop table, add a new `<td>` after the Teles `<td>`:

```tsx
<td style={{ padding: '13px 0' }}>
  {(() => {
    const { priceTotal, paid } = parsePayments(c.payments);
    if (priceTotal === null || priceTotal === 0) return <Mono size={11} color={T.ink3}>—</Mono>;
    const outstanding = Math.max(0, priceTotal - paid);
    return outstanding > 0
      ? <Mono size={11} color={T.gold}>€{outstanding.toLocaleString('ca-ES')}</Mono>
      : <Mono size={11} color={T.ink3}>✓</Mono>;
  })()}
</td>
```

- [ ] **Step 3.3: Verify manually**

```bash
cd frontend && npm run dev
```

1. Click column header "Dies" → list reorders ascending; click again → descending
2. Click "Clienta" → sorts alphabetically; click "Estat" → sorts by pipeline order
3. A client with ≤ 14 days should have a red left border
4. A client with 15–30 days should have a gold left border
5. Pendent column shows outstanding amount or ✓

- [ ] **Step 3.4: Final commit**

```bash
git add frontend/src/screens/ClientsScreen.tsx
git commit -m "feat(clients): outstanding balance column + import parsePayments"
```

---

## Self-Review

**Spec coverage:**
- Sortable columns (name, status, days_until) ✓
- Sort direction toggle ✓
- Active sort indicator (arrow) ✓
- Urgency: ≤ 14 days critical (red), ≤ 30 days warning (gold) ✓
- Skip urgency for 'entregada' status ✓
- Outstanding balance column ✓
- Mobile urgency border ✓
- No new API needed ✓

**Note:** The "Pendent" column header was added to the `<thead>` map in Task 1. If implementing Task 3 without Task 1, add the header manually to the existing `['Clienta', 'Peça', 'Estat', 'Boda', 'Dies', 'Teles']` array as `'Pendent'` at the end.

**Type consistency:** `urgency` function takes `days: number, status: string` — both available on every `Client` object. `parsePayments` imported from `clientHelpers` and used inline in IIFE to avoid polluting the map callback scope.
