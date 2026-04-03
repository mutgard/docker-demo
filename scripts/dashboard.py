#!/usr/bin/env python3
"""
Juliette by Julia Arnau — Operations Dashboard
Run: python3 scripts/dashboard.py
Then open: http://localhost:8765
"""

import os, re, json
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import date

ROOT = Path(__file__).parent.parent / "atelier"
TODAY = str(date.today())


# ── Markdown parsers ──────────────────────────────────────────────────────────

def field(text, label):
    """Extract a field value like '- **Label:** value'"""
    m = re.search(rf"\*\*{re.escape(label)}:\*\*\s*(.+)", text)
    return m.group(1).strip() if m else ""

def load_clients():
    clients = []
    clients_dir = ROOT / "clients"
    for slug_dir in sorted(clients_dir.iterdir()):
        if not slug_dir.is_dir() or slug_dir.name.startswith("_"):
            continue
        profile = slug_dir / "profile.md"
        if not profile.exists():
            continue
        text = profile.read_text()
        name_m = re.search(r"^# Client:\s*(.+)", text, re.MULTILINE)
        name = name_m.group(1).strip() if name_m else slug_dir.name.title()

        # Orders
        orders_dir = slug_dir / "orders"
        active_order = None
        if orders_dir.exists():
            for o in sorted(orders_dir.glob("*.md")):
                if o.name.startswith("_"):
                    continue
                ot = o.read_text()
                stage = field(ot, "Current stage")
                if stage and stage.lower() not in ("delivered", "cancelled"):
                    active_order = {"id": o.stem, "stage": stage}
                    break

        # Last comms
        comms_dir = slug_dir / "comms"
        last_contact = ""
        if comms_dir.exists():
            logs = sorted(comms_dir.glob("*.md"), reverse=True)
            if logs:
                last_contact = logs[0].stem[:10]

        clients.append({
            "slug": slug_dir.name,
            "name": name,
            "phone": field(text, "Phone"),
            "whatsapp": field(text, "WhatsApp"),
            "wedding_date": field(text, "Wedding date"),
            "tags": field(text, "Tags"),
            "active_order": active_order,
            "last_contact": last_contact,
            "notes": field(text, "Notes"),
        })
    return clients

def load_appointments():
    appts = []
    appt_dir = ROOT / "appointments"
    for f in sorted(appt_dir.glob("*.md")):
        if f.name.startswith("_"):
            continue
        text = f.read_text()
        date_str = f.stem[:10]
        name_m = re.search(r"^# Appointment:.*?—\s*(.+)", text, re.MULTILINE)
        name = name_m.group(1).strip() if name_m else ""
        appts.append({
            "date": date_str,
            "name": name,
            "time": field(text, "Time"),
            "type": field(text, "Type"),
            "past": date_str < TODAY,
        })
    return appts

def load_finances():
    invoices = []
    inv_dir = ROOT / "finances" / "invoices"
    if not inv_dir.exists():
        return invoices
    for f in sorted(inv_dir.glob("*.md")):
        text = f.read_text()
        client_m = re.search(r"\[\[clients/(.+?)/", text)
        client = client_m.group(1).title() if client_m else ""
        invoices.append({
            "id": f.stem,
            "client": client,
            "total": field(text, "Total"),
            "paid": field(text, "Total paid"),
            "outstanding": field(text, "Balance outstanding"),
        })
    return invoices


# ── HTML renderer ─────────────────────────────────────────────────────────────

def stage_color(stage):
    colors = {
        "consultation": "#e0e7ff",
        "design": "#fef3c7",
        "toile": "#fce7f3",
        "toile-fitting": "#fce7f3",
        "construction": "#d1fae5",
        "first-fitting": "#bbf7d0",
        "alterations-1": "#fef9c3",
        "second-fitting": "#bbf7d0",
        "alterations-2": "#fef9c3",
        "final-fitting": "#a7f3d0",
        "ready": "#6ee7b7",
        "delivered": "#d1d5db",
    }
    return colors.get(stage.lower(), "#f3f4f6") if stage else "#f3f4f6"

def render_html(clients, appointments, finances):
    upcoming = [a for a in appointments if not a["past"]]
    past = [a for a in appointments if a["past"]]
    leads = [c for c in clients if not c["active_order"]]
    active = [c for c in clients if c["active_order"]]

    def client_card(c):
        order_badge = ""
        if c["active_order"]:
            stage = c["active_order"]["stage"] or "—"
            color = stage_color(stage)
            order_badge = f'<span class="badge" style="background:{color}">{stage}</span>'
        tags = c["tags"]
        tag_html = " ".join(f'<span class="tag">{t.strip()}</span>' for t in tags.split(",") if t.strip()) if tags else ""
        contact = c["whatsapp"] or c["phone"] or "—"
        return f"""
        <div class="card" onclick="window.open('','_blank')">
          <div class="card-name">{c["name"]}</div>
          <div class="card-detail">💍 {c["wedding_date"] or "Date TBC"}</div>
          <div class="card-detail">📞 {contact}</div>
          {f'<div class="card-detail muted">{c["notes"][:60]}{"…" if len(c["notes"])>60 else ""}</div>' if c["notes"] else ""}
          <div class="card-footer">
            {order_badge}
            {tag_html}
            {f'<span class="muted" style="font-size:11px">Last contact: {c["last_contact"]}</span>' if c["last_contact"] else ""}
          </div>
        </div>"""

    def appt_row(a, highlight=False):
        bg = "#f0fdf4" if highlight else "white"
        return f"""
        <tr style="background:{bg}">
          <td><strong>{a["date"]}</strong></td>
          <td>{a["time"] or "TBC"}</td>
          <td>{a["name"]}</td>
          <td><span class="badge" style="background:#e0e7ff">{a["type"]}</span></td>
        </tr>"""

    upcoming_rows = "".join(appt_row(a, True) for a in upcoming) or '<tr><td colspan="4" class="muted">No upcoming appointments</td></tr>'
    past_rows = "".join(appt_row(a) for a in reversed(past)) or '<tr><td colspan="4" class="muted">No past appointments</td></tr>'

    finance_rows = ""
    for inv in finances:
        finance_rows += f"""
        <tr>
          <td>{inv["id"]}</td>
          <td>{inv["client"]}</td>
          <td>{inv["total"] or "—"}</td>
          <td>{inv["paid"] or "—"}</td>
          <td><strong style="color:#dc2626">{inv["outstanding"] or "—"}</strong></td>
        </tr>"""
    if not finance_rows:
        finance_rows = '<tr><td colspan="5" class="muted">No invoices yet</td></tr>'

    active_cards = "".join(client_card(c) for c in active) or '<p class="muted">No active orders</p>'
    lead_cards = "".join(client_card(c) for c in leads) or '<p class="muted">No leads</p>'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Juliette by Julia Arnau</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: #faf9f7; color: #1a1a1a; }}
  header {{ background: #1a1a1a; color: #f5f0ea; padding: 24px 32px; display: flex; align-items: baseline; gap: 16px; }}
  header h1 {{ font-size: 22px; font-weight: 500; letter-spacing: 0.04em; }}
  header .sub {{ font-size: 13px; color: #888; }}
  .stats {{ display: flex; gap: 1px; background: #e5e7eb; border-bottom: 1px solid #e5e7eb; }}
  .stat {{ flex: 1; background: white; padding: 18px 24px; }}
  .stat-num {{ font-size: 28px; font-weight: 600; color: #1a1a1a; }}
  .stat-label {{ font-size: 12px; color: #6b7280; margin-top: 2px; text-transform: uppercase; letter-spacing: 0.05em; }}
  main {{ padding: 32px; max-width: 1200px; margin: 0 auto; }}
  section {{ margin-bottom: 40px; }}
  h2 {{ font-size: 14px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; color: #6b7280; margin-bottom: 16px; border-bottom: 1px solid #e5e7eb; padding-bottom: 8px; }}
  .cards {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 16px; }}
  .card {{ background: white; border: 1px solid #e5e7eb; border-radius: 10px; padding: 16px; cursor: pointer; transition: box-shadow 0.15s; }}
  .card:hover {{ box-shadow: 0 4px 12px rgba(0,0,0,0.08); }}
  .card-name {{ font-size: 16px; font-weight: 600; margin-bottom: 8px; }}
  .card-detail {{ font-size: 13px; color: #4b5563; margin-bottom: 4px; }}
  .card-footer {{ margin-top: 12px; display: flex; flex-wrap: wrap; gap: 6px; align-items: center; }}
  .badge {{ display: inline-block; padding: 2px 8px; border-radius: 999px; font-size: 11px; font-weight: 500; }}
  .tag {{ display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; background: #f3f4f6; color: #374151; }}
  table {{ width: 100%; border-collapse: collapse; background: white; border: 1px solid #e5e7eb; border-radius: 10px; overflow: hidden; }}
  th {{ text-align: left; padding: 10px 16px; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: #6b7280; background: #f9fafb; border-bottom: 1px solid #e5e7eb; }}
  td {{ padding: 12px 16px; font-size: 14px; border-bottom: 1px solid #f3f4f6; }}
  tr:last-child td {{ border-bottom: none; }}
  .muted {{ color: #9ca3af; font-size: 13px; }}
  .today {{ font-size: 12px; color: #9ca3af; }}
</style>
</head>
<body>
<header>
  <h1>Juliette by Julia Arnau</h1>
  <span class="sub">Operations · {TODAY}</span>
</header>

<div class="stats">
  <div class="stat">
    <div class="stat-num">{len(active)}</div>
    <div class="stat-label">Active orders</div>
  </div>
  <div class="stat">
    <div class="stat-num">{len(leads)}</div>
    <div class="stat-label">Leads</div>
  </div>
  <div class="stat">
    <div class="stat-num">{len(upcoming)}</div>
    <div class="stat-label">Upcoming appointments</div>
  </div>
  <div class="stat">
    <div class="stat-num">{len(finances)}</div>
    <div class="stat-label">Open invoices</div>
  </div>
</div>

<main>

  <section>
    <h2>Active Orders</h2>
    <div class="cards">{active_cards}</div>
  </section>

  <section>
    <h2>Leads</h2>
    <div class="cards">{lead_cards}</div>
  </section>

  <section>
    <h2>Upcoming Appointments</h2>
    <table>
      <thead><tr><th>Date</th><th>Time</th><th>Client</th><th>Type</th></tr></thead>
      <tbody>{upcoming_rows}</tbody>
    </table>
  </section>

  <section>
    <h2>Past Appointments</h2>
    <table>
      <thead><tr><th>Date</th><th>Time</th><th>Client</th><th>Type</th></tr></thead>
      <tbody>{past_rows}</tbody>
    </table>
  </section>

  <section>
    <h2>Invoices</h2>
    <table>
      <thead><tr><th>Invoice</th><th>Client</th><th>Total</th><th>Paid</th><th>Outstanding</th></tr></thead>
      <tbody>{finance_rows}</tbody>
    </table>
  </section>

</main>
</body>
</html>"""


# ── HTTP server ───────────────────────────────────────────────────────────────

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        clients = load_clients()
        appointments = load_appointments()
        finances = load_finances()
        html = render_html(clients, appointments, finances)
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode())

    def log_message(self, fmt, *args):
        pass  # silence request logs

if __name__ == "__main__":
    port = 8765
    print(f"Dashboard running → http://localhost:{port}")
    print("Reads live from atelier/ — just refresh the browser to update.")
    print("Ctrl+C to stop.\n")
    HTTPServer(("", port), Handler).serve_forever()
