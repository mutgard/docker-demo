# Roadmap View — Design Spec

**Date:** 2026-04-21
**Status:** Approved

---

## Overview

A monthly calendar view (`RoadmapScreen`) showing all planned atelier events: client appointments, fabric/supplier deliveries, and wedding days. Events are a unified read model (`GET /api/events`) while writes go to typed sub-routes. The same event data is reused in the client profile tab, replacing the current generic KV appointment list.

---

## Data Model

### New `deliveries` table

| field | type | notes |
|---|---|---|
| `id` | int PK | |
| `client_id` | int FK nullable | null = general studio purchase |
| `supplier` | str | e.g. "Teles Girona" |
| `description` | str | e.g. "Chantilly lace 3m" |
| `expected_date` | date | |
| `received` | bool | default false |

### `appointments` table — migration

Add a `date` date column (nullable). Existing rows are unaffected. Appointments without a `date` will not appear in the roadmap or in the profile EventList until migrated. The `{label, value}` KV structure remains in the database but the profile tab UI switches to the EventList — old dateless appointments won't be visible until given a date.

### `AtelierEvent` shape (read model)

```ts
export type EventType = 'appointment' | 'delivery' | 'wedding';

export interface AtelierEvent {
  id: number;
  type: EventType;
  date: string;           // YYYY-MM-DD
  title: string;
  client_id: number | null;
  client_name: string | null;
  order_id?: string;      // appointments only
  supplier?: string;      // deliveries only
}
```

---

## API

### Read

`GET /api/events`
Query params: `from` (YYYY-MM-DD), `to` (YYYY-MM-DD), `client_id` (optional int).
Returns a flat, date-sorted list of `AtelierEvent`. The backend aggregates from three sources:
- `appointments` where `date` is not null
- `deliveries` using `expected_date`
- `clients` where `wedding_date` is not null (one wedding event per client)

### Write — typed sub-routes

| method | route | action |
|---|---|---|
| `POST` | `/api/appointments` | create appointment (requires `date`) |
| `PATCH` | `/api/appointments/{id}` | update appointment |
| `DELETE` | `/api/appointments/{id}` | delete appointment |
| `POST` | `/api/deliveries` | create delivery |
| `PATCH` | `/api/deliveries/{id}` | update delivery |
| `DELETE` | `/api/deliveries/{id}` | delete delivery |

Wedding events are not independently created — they derive from `client.wedding_date`. Editing a wedding event via `PATCH /api/clients/{id}` (already exists).

---

## Frontend

### New screen: `RoadmapScreen`

Added as screen `'roadmap'` in `App.tsx`. New sidebar entry: `05 Agenda`.

**Composition:**

```
RoadmapScreen
├── CalendarHeader       — month/year title (serif), ChevronLeft/Right nav, today button, + add event button
├── CalendarGrid         — 7-col Mon–Sun grid
│   └── DayCell[]        — date number + up to 3 EventChips, overflow count chip
│       └── EventChip    — color-coded pill (click → EventPopover)
│           └── EventPopover (shadcn Popover)
│               ├── event detail (title, client, date, order/supplier)
│               ├── edit icon → EditEventDialog
│               └── delete button → DeleteConfirmDialog (shadcn AlertDialog)
└── CreateEventDialog    — shadcn Dialog (shared with profile tab)
```

**EventChip color coding** (using existing tokens):
- `appointment` → `T.accent` (red)
- `delivery` → `T.gold`
- `wedding` → `T.ink`

**shadcn components**: `Popover`, `Button`, `Dialog`, `AlertDialog`
**Lucide icons**: `ChevronLeft`, `ChevronRight`, `CalendarDays`, `Truck`, `Heart`, `Plus`, `Pencil`, `Trash2`

### `CreateEventDialog` / `EditEventDialog`

Single dialog component. When `eventId` prop is present → edit mode (pre-populated, calls PATCH). When absent → create mode (calls POST).

Fields:
- **Type** — segment control: Appointment / Delivery / Wedding
- **Date** — `<input type="date">`
- **Title** — text input
- **Client** — dropdown (locked when opened from profile tab)
- **Conditional**:
  - Appointment → Order ID (optional)
  - Delivery → Supplier (required), client optional
  - Wedding → no extra fields. On save, calls `PATCH /api/clients/{client_id}` to update `wedding_date`. Client field is required. If the client already has a wedding date, it is overwritten (a client has exactly one wedding day).

Opened from:
1. Roadmap `+` button or empty day cell click (pre-fills date)
2. Profile tab "Add event" button (pre-fills `client_id`)
3. `EventPopover` edit icon (edit mode, pre-fills all fields)

### Profile tab change

The existing appointments KV section is replaced by an `EventList` component: a vertical list of upcoming events for that client, fetched from `GET /api/events?client_id=X&from=today`. Each row reuses `EventChip` and shows date + title. Includes "Add event" button that opens `CreateEventDialog` with `client_id` pre-filled.

---

## Dependencies to install

```
shadcn/ui (Popover, Button, Dialog, AlertDialog)
lucide-react
```

The app currently has no component library. shadcn components will be added to `frontend/src/components/ui/` following shadcn conventions. They must respect the existing token palette (`T.*`) — override shadcn CSS variables to match.

---

## Out of scope

- Recurring events
- Event notifications / reminders
- Drag-and-drop rescheduling
- Multi-week or year-view modes
