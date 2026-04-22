# Order Status Workflow UI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give Julia a clear visual pipeline in ProfileScreen showing the 4 order stages and a single "Avançar" button to advance the client to the next stage.

**Architecture:** Replace the plain `<Badge>` in the profile hero with a horizontal pipeline component that shows all 4 stages (`prospect → sense-paga → clienta → entregada`), highlights the current one, and renders an "Avançar" button for the next stage. On click, call the existing `PATCH /clients/{id}` endpoint. No new backend routes, no new files — only `ProfileScreen.tsx` changes.

**Tech Stack:** React + TypeScript, existing `api.patchClient`, existing `T` token system.

---

## File Map

**Modified only:**
- `frontend/src/screens/ProfileScreen.tsx` — replace badge with pipeline component + advance handler

---

## Task 1: Status pipeline component

**Files:**
- Modify: `frontend/src/screens/ProfileScreen.tsx`

- [ ] **Step 1.1: Define pipeline constants**

At the top of the `ProfileScreen` function body (before the state declarations), add:

```tsx
const PIPELINE: { value: import('../types').ClientStatus; label: string }[] = [
  { value: 'prospect',   label: 'Prospect' },
  { value: 'sense-paga', label: 'Sense paga' },
  { value: 'clienta',    label: 'Clienta' },
  { value: 'entregada',  label: 'Entregada' },
];

const currentIdx = PIPELINE.findIndex(s => s.value === c.status);
const nextStage = currentIdx < PIPELINE.length - 1 ? PIPELINE[currentIdx + 1] : null;
```

Note: `c` here is the local state variable `const [c, setC] = useState<Client>(initial)`. Since `PIPELINE` and `currentIdx` depend on `c`, they must be inside the component function, not at module level.

- [ ] **Step 1.2: Add advanceStatus handler**

After `saveEdit`, add:

```tsx
const advanceStatus = async () => {
  if (!nextStage) return;
  await api.patchClient(c.id, { status: nextStage.value });
  const updated = await api.getClient(c.id);
  setC(updated);
  onRefresh();
};
```

- [ ] **Step 1.3: Commit**

```bash
git add frontend/src/screens/ProfileScreen.tsx
git commit -m "feat(profile): pipeline constants + advanceStatus handler"
```

---

## Task 2: Render the pipeline in the hero section

**Files:**
- Modify: `frontend/src/screens/ProfileScreen.tsx` — hero badge area

- [ ] **Step 2.1: Replace the Badge with a pipeline strip**

In the hero section, find the `<div style={{ marginTop: 6, display: 'flex', gap: 8, flexWrap: 'wrap', alignItems: 'center' }}>` block that currently renders `<Badge status={c.status} />`. Replace that entire `<div>` with:

```tsx
<div style={{ marginTop: 10 }}>
  {/* Pipeline strip */}
  <div style={{ display: 'flex', alignItems: 'center', gap: 0, flexWrap: 'wrap', rowGap: 4 }}>
    {PIPELINE.map((stage, i) => {
      const isCurrent = i === currentIdx;
      const isPast = i < currentIdx;
      const isNext = i === currentIdx + 1;
      const isLast = i === PIPELINE.length - 1;
      return (
        <div key={stage.value} style={{ display: 'flex', alignItems: 'center' }}>
          <div style={{
            padding: '3px 10px',
            border: `1px ${isCurrent ? 'solid' : isPast ? 'solid' : 'dashed'} ${isCurrent ? T.accent : isPast ? T.hairline2 : T.hairline}`,
            background: isCurrent ? T.accent : 'transparent',
            color: isCurrent ? T.paper : isPast ? T.ink3 : T.ink3,
            fontFamily: T.mono, fontSize: 9, letterSpacing: 0.8, textTransform: 'uppercase',
            whiteSpace: 'nowrap',
            opacity: isPast ? 0.5 : 1,
          }}>
            {isPast ? '✓ ' : ''}{stage.label}
          </div>
          {!isLast && (
            <div style={{ width: 12, height: 1, background: T.hairline, flexShrink: 0 }} />
          )}
        </div>
      );
    })}
  </div>

  {/* Next-stage action button */}
  {nextStage && !editing && (
    <button
      onClick={advanceStatus}
      style={{
        marginTop: 10,
        padding: '6px 14px',
        background: 'transparent',
        border: `1px solid ${T.ink}`,
        color: T.ink,
        fontFamily: T.mono, fontSize: 9, letterSpacing: 0.8,
        textTransform: 'uppercase', cursor: 'pointer',
        display: 'inline-flex', alignItems: 'center', gap: 6,
      }}
    >
      Avançar → {nextStage.label}
    </button>
  )}

  {/* Subtitle: upcoming event */}
  {!editing && clientEvents.length > 0 && (
    <div style={{ marginTop: 6 }}>
      <Mono size={10} color={T.ink3}>
        {clientEvents[0].title} · {clientEvents[0].date}
      </Mono>
    </div>
  )}
</div>
```

- [ ] **Step 2.2: Remove the now-redundant `<Badge>` import from primitives (only if Badge is no longer used elsewhere in ProfileScreen)**

Check the full ProfileScreen for other uses of `Badge`. The original hero badge has been replaced. If there are no other uses, remove `Badge` from the destructured import:

```tsx
// Before:
import { Label, Mono, Serif, Badge, Swatch, Checkbox } from '../components/primitives';

// After (if Badge unused):
import { Label, Mono, Serif, Swatch, Checkbox } from '../components/primitives';
```

If Badge appears elsewhere, leave the import untouched.

- [ ] **Step 2.3: Verify visually**

```bash
cd frontend && npm run dev
```

1. Open a `prospect` client: pipeline shows `Prospect` highlighted, 3 others dimmed; "Avançar → Sense paga" button visible
2. Click "Avançar → Sense paga": badge updates, next button shows "Avançar → Clienta"
3. Advance to `clienta`: next button shows "Avançar → Entregada"
4. Advance to `entregada`: no "Avançar" button visible; all 4 stages show with checkmarks on past ones
5. In edit mode, the "Avançar" button is hidden (editing controls take priority)

- [ ] **Step 2.4: Verify backend test still passes**

```bash
cd backend && python -m pytest tests/test_clients.py::test_patch_client_status -v
```

Expected: PASS

- [ ] **Step 2.5: Commit**

```bash
git add frontend/src/screens/ProfileScreen.tsx
git commit -m "feat(profile): order status pipeline — visual stages + advance button"
```

---

## Self-Review

**Spec coverage:**
- Visual pipeline showing all 4 stages ✓
- Current stage highlighted (red background) ✓
- Past stages shown with ✓ prefix + faded ✓
- Future stages shown dashed + faded ✓
- "Avançar → [next stage]" button ✓
- Calls PATCH /clients/{id} on advance ✓
- Refreshes client state after advance ✓
- No "Avançar" button when already at `entregada` ✓
- Button hidden during edit mode ✓
- No new files ✓

**Type consistency:** `nextStage` is `{ value: ClientStatus; label: string } | null`. `advanceStatus` passes `nextStage.value` which is `ClientStatus`, accepted by `api.patchClient` which takes `Partial<Client>`. `PIPELINE` is defined inside the component so it sees the current `c.status` on every render.
