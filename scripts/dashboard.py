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


# ── Data loaders ──────────────────────────────────────────────────────────────

def field(text, label):
    m = re.search(rf"\*\*{re.escape(label)}:\*\*\s*(.+)", text)
    return m.group(1).strip() if m else ""

def load_clients():
    clients = []
    clients_dir = ROOT / "clients"
    if not clients_dir.exists():
        return clients
    for slug_dir in sorted(clients_dir.iterdir()):
        if not slug_dir.is_dir() or slug_dir.name.startswith("_"):
            continue
        profile = slug_dir / "profile.md"
        if not profile.exists():
            continue
        text = profile.read_text()
        name_m = re.search(r"^# Client:\s*(.+)", text, re.MULTILINE)
        name = name_m.group(1).strip() if name_m else slug_dir.name.title()
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
    if not appt_dir.exists():
        return appts
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
        client = client_m.group(1).replace("-", " ").title() if client_m else ""
        invoices.append({
            "id": f.stem,
            "client": client,
            "total": field(text, "Total"),
            "paid": field(text, "Total paid"),
            "outstanding": field(text, "Balance outstanding"),
        })
    return invoices


# ── HTML ──────────────────────────────────────────────────────────────────────

STAGE_COLORS = {
    "consultation":  ("#EDE9FE", "#7C3AED"),
    "design":        ("#FEF3C7", "#D97706"),
    "toile":         ("#FCE7F3", "#DB2777"),
    "toile-fitting": ("#FCE7F3", "#DB2777"),
    "construction":  ("#D1FAE5", "#059669"),
    "first-fitting": ("#D1FAE5", "#059669"),
    "alterations-1": ("#FEF9C3", "#CA8A04"),
    "second-fitting":("#D1FAE5", "#059669"),
    "alterations-2": ("#FEF9C3", "#CA8A04"),
    "final-fitting": ("#A7F3D0", "#047857"),
    "ready":         ("#6EE7B7", "#065F46"),
    "delivered":     ("#F3F4F6", "#6B7280"),
}

def stage_badge(stage):
    if not stage:
        return ""
    bg, fg = STAGE_COLORS.get(stage.lower(), ("#F3F4F6", "#6B7280"))
    return f'<span class="stage-badge" style="background:{bg};color:{fg}">{stage}</span>'

def initials(name):
    parts = name.strip().split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[-1][0]).upper()
    return name[:2].upper() if name else "??"

def avatar_color(name):
    colors = ["#C9B8A8","#B5C4B1","#C4B7CB","#C8B8A2","#B8C4C8","#CDB5BD","#B5C4B5"]
    return colors[sum(ord(c) for c in name) % len(colors)]

def render_client_card(c):
    badge = stage_badge(c["active_order"]["stage"] if c["active_order"] else "")
    order_label = f'<div class="card-meta">{badge}</div>' if badge else '<div class="card-meta"><span class="lead-tag">Lead</span></div>'
    contact = c["whatsapp"] or c["phone"] or ""
    wedding = c["wedding_date"] or "Wedding date TBC"
    note_html = f'<p class="card-note">{c["notes"][:55]}{"…" if len(c["notes"]) > 55 else ""}</p>' if c["notes"] else ""
    contact_html = f'<p class="card-contact">{contact}</p>' if contact else ""
    last_html = f'<p class="card-last">Last contact {c["last_contact"]}</p>' if c["last_contact"] else ""
    av_bg = avatar_color(c["name"])
    ini = initials(c["name"])
    return f"""
    <div class="client-card">
      <div class="card-top">
        <div class="avatar" style="background:{av_bg}">{ini}</div>
        <div class="card-info">
          <h3 class="card-name">{c["name"]}</h3>
          <p class="card-wedding">&#9674; {wedding}</p>
        </div>
      </div>
      {note_html}
      {contact_html}
      {last_html}
      {order_label}
    </div>"""

def render_html(clients, appointments, finances):
    upcoming = [a for a in appointments if not a["past"]]
    active = [c for c in clients if c["active_order"]]
    leads  = [c for c in clients if not c["active_order"]]

    # Stats
    stat_orders = len(active)
    stat_leads  = len(leads)
    stat_appts  = len(upcoming)
    stat_inv    = len([f for f in finances if f["outstanding"] and f["outstanding"] not in ("—", "", "0")])

    # Client cards
    active_cards = "".join(render_client_card(c) for c in active)
    lead_cards   = "".join(render_client_card(c) for c in leads)

    clients_html = ""
    if active_cards:
        clients_html += f'<h2 class="section-label">Active orders</h2><div class="cards-grid">{active_cards}</div>'
    if lead_cards:
        clients_html += f'<h2 class="section-label" style="margin-top:32px">Leads</h2><div class="cards-grid">{lead_cards}</div>'
    if not clients_html:
        clients_html = '<div class="empty">No clients yet.</div>'

    # Upcoming appointments rows
    appt_rows = ""
    for a in upcoming:
        appt_rows += f"""
        <div class="list-row">
          <div class="list-date">{a["date"]}</div>
          <div class="list-main">
            <span class="list-name">{a["name"]}</span>
            <span class="list-sub">{a["type"] or ""}{" · " + a["time"] if a["time"] and a["time"] != "TBC" else ""}</span>
          </div>
        </div>"""
    appts_html = appt_rows or '<div class="empty">No upcoming appointments.</div>'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Juliette by Julia Arnau</title>
<style>
  :root {{
    --bg: #FAF8F5;
    --surface: #FFFFFF;
    --border: #EDE9E3;
    --text: #1C1917;
    --muted: #78716C;
    --accent: #9D7B5A;
    --accent-light: #F5EFE8;
    --nav-h: 60px;
    --header-h: 64px;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; -webkit-tap-highlight-color: transparent; }}
  html, body {{ height: 100%; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    background: var(--bg);
    color: var(--text);
    display: flex;
    flex-direction: column;
  }}

  /* ── Header ── */
  header {{
    height: var(--header-h);
    background: var(--surface);
    border-bottom: 1px solid var(--border);
    display: flex;
    align-items: center;
    padding: 0 20px;
    gap: 12px;
    position: sticky;
    top: 0;
    z-index: 10;
  }}
  .logo-mark {{
    width: 32px; height: 32px;
    background: var(--text);
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    color: #FAF8F5;
    font-size: 13px;
    letter-spacing: 0.02em;
    flex-shrink: 0;
  }}
  .brand {{ flex: 1; }}
  .brand-name {{
    font-size: 15px;
    font-weight: 600;
    letter-spacing: 0.01em;
    color: var(--text);
  }}
  .brand-sub {{
    font-size: 11px;
    color: var(--muted);
    margin-top: 1px;
  }}

  /* ── Stats bar ── */
  .stats {{
    display: flex;
    background: var(--surface);
    border-bottom: 1px solid var(--border);
    overflow-x: auto;
    scrollbar-width: none;
  }}
  .stats::-webkit-scrollbar {{ display: none; }}
  .stat {{
    flex: 1;
    min-width: 80px;
    padding: 14px 16px;
    text-align: center;
    border-right: 1px solid var(--border);
  }}
  .stat:last-child {{ border-right: none; }}
  .stat-num {{
    font-size: 24px;
    font-weight: 700;
    color: var(--text);
    line-height: 1;
  }}
  .stat-label {{
    font-size: 10px;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-top: 4px;
  }}

  /* ── Tab nav ── */
  .tab-nav {{
    background: var(--surface);
    border-bottom: 1px solid var(--border);
    display: flex;
    overflow-x: auto;
    scrollbar-width: none;
    padding: 0 4px;
  }}
  .tab-nav::-webkit-scrollbar {{ display: none; }}
  .tab {{
    padding: 12px 16px;
    font-size: 13px;
    font-weight: 500;
    color: var(--muted);
    cursor: pointer;
    border-bottom: 2px solid transparent;
    white-space: nowrap;
    user-select: none;
    transition: color 0.15s;
  }}
  .tab.active {{
    color: var(--text);
    border-bottom-color: var(--text);
  }}
  .tab .wip {{
    display: inline-block;
    margin-left: 5px;
    font-size: 9px;
    background: #F5F5F4;
    color: var(--muted);
    padding: 1px 5px;
    border-radius: 99px;
    vertical-align: middle;
  }}

  /* ── Content ── */
  .content {{ flex: 1; overflow-y: auto; padding: 20px; }}
  .panel {{ display: none; }}
  .panel.active {{ display: block; }}

  /* ── Section label ── */
  .section-label {{
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--muted);
    margin-bottom: 12px;
  }}

  /* ── Client cards ── */
  .cards-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 12px;
  }}
  .client-card {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 16px;
    transition: box-shadow 0.15s;
  }}
  .client-card:hover {{ box-shadow: 0 2px 12px rgba(0,0,0,0.07); }}
  .card-top {{
    display: flex;
    gap: 12px;
    align-items: flex-start;
    margin-bottom: 10px;
  }}
  .avatar {{
    width: 42px; height: 42px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 14px;
    font-weight: 600;
    color: #fff;
    flex-shrink: 0;
    letter-spacing: 0.03em;
  }}
  .card-info {{ flex: 1; min-width: 0; }}
  .card-name {{
    font-size: 15px;
    font-weight: 600;
    color: var(--text);
    margin-bottom: 3px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }}
  .card-wedding {{
    font-size: 12px;
    color: var(--muted);
  }}
  .card-note {{
    font-size: 12px;
    color: var(--muted);
    margin-bottom: 8px;
    line-height: 1.4;
  }}
  .card-contact {{
    font-size: 12px;
    color: var(--muted);
    margin-bottom: 4px;
  }}
  .card-last {{
    font-size: 11px;
    color: #A8A29E;
    margin-bottom: 10px;
  }}
  .card-meta {{ display: flex; flex-wrap: wrap; gap: 6px; }}
  .stage-badge {{
    display: inline-block;
    padding: 3px 10px;
    border-radius: 99px;
    font-size: 11px;
    font-weight: 500;
  }}
  .lead-tag {{
    display: inline-block;
    padding: 3px 10px;
    border-radius: 99px;
    font-size: 11px;
    font-weight: 500;
    background: var(--accent-light);
    color: var(--accent);
  }}

  /* ── Appointments list ── */
  .list-row {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 14px 16px;
    display: flex;
    gap: 14px;
    align-items: center;
    margin-bottom: 8px;
  }}
  .list-date {{
    font-size: 12px;
    font-weight: 600;
    color: var(--muted);
    min-width: 80px;
  }}
  .list-main {{ flex: 1; }}
  .list-name {{
    display: block;
    font-size: 14px;
    font-weight: 600;
    color: var(--text);
  }}
  .list-sub {{
    font-size: 12px;
    color: var(--muted);
    margin-top: 2px;
    display: block;
  }}

  /* ── Under construction ── */
  .wip-panel {{
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 64px 24px;
    text-align: center;
  }}
  .wip-icon {{
    font-size: 40px;
    margin-bottom: 16px;
    opacity: 0.4;
  }}
  .wip-title {{
    font-size: 16px;
    font-weight: 600;
    color: var(--text);
    margin-bottom: 6px;
  }}
  .wip-sub {{
    font-size: 13px;
    color: var(--muted);
    max-width: 240px;
    line-height: 1.5;
  }}

  /* ── Empty state ── */
  .empty {{
    font-size: 13px;
    color: var(--muted);
    padding: 32px 0;
    text-align: center;
  }}

  @media (max-width: 480px) {{
    .cards-grid {{ grid-template-columns: 1fr; }}
    .stat-num {{ font-size: 20px; }}
  }}
</style>
</head>
<body>

<header>
  <div class="logo-mark">J</div>
  <div class="brand">
    <div class="brand-name">Juliette by Julia Arnau</div>
    <div class="brand-sub">{TODAY}</div>
  </div>
</header>

<div class="stats">
  <div class="stat">
    <div class="stat-num">{stat_orders}</div>
    <div class="stat-label">Orders</div>
  </div>
  <div class="stat">
    <div class="stat-num">{stat_leads}</div>
    <div class="stat-label">Leads</div>
  </div>
  <div class="stat">
    <div class="stat-num">{stat_appts}</div>
    <div class="stat-label">Upcoming</div>
  </div>
  <div class="stat">
    <div class="stat-num">{stat_inv}</div>
    <div class="stat-label">Unpaid</div>
  </div>
</div>

<div class="tab-nav">
  <div class="tab active" data-panel="clients">Clients</div>
  <div class="tab" data-panel="appointments">Appointments</div>
  <div class="tab" data-panel="orders">Orders <span class="wip">soon</span></div>
  <div class="tab" data-panel="finances">Finances <span class="wip">soon</span></div>
  <div class="tab" data-panel="inbox">Inbox <span class="wip">soon</span></div>
</div>

<div class="content">

  <div class="panel active" id="panel-clients">
    {clients_html}
  </div>

  <div class="panel" id="panel-appointments">
    <h2 class="section-label">Upcoming</h2>
    {appts_html}
  </div>

  <div class="panel" id="panel-orders">
    <div class="wip-panel">
      <div class="wip-icon">&#9999;</div>
      <div class="wip-title">Orders</div>
      <div class="wip-sub">Full order management with stages and timelines — coming soon.</div>
    </div>
  </div>

  <div class="panel" id="panel-finances">
    <div class="wip-panel">
      <div class="wip-icon">&#128176;</div>
      <div class="wip-title">Finances</div>
      <div class="wip-sub">Invoices, deposits, outstanding balances — coming soon.</div>
    </div>
  </div>

  <div class="panel" id="panel-inbox">
    <div class="wip-panel">
      <div class="wip-icon">&#128172;</div>
      <div class="wip-title">Inbox</div>
      <div class="wip-sub">Unified inbox for WhatsApp, email, and web form — coming soon.</div>
    </div>
  </div>

</div>

<script>
  document.querySelectorAll('.tab').forEach(tab => {{
    tab.addEventListener('click', () => {{
      document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
      tab.classList.add('active');
      document.getElementById('panel-' + tab.dataset.panel).classList.add('active');
    }});
  }});
</script>
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
        pass

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"Dashboard running → http://localhost:{port}")
    print("Reads live from atelier/ — just refresh to update.")
    print("Ctrl+C to stop.\n")
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()
