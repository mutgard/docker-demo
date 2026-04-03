#!/usr/bin/env python3
"""
Juliette by Julia Arnau — Operations Dashboard
Run: python3 scripts/dashboard.py
Then open: http://localhost:8765
"""

import os, re, json, urllib.parse
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import date, datetime

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

def load_inbox():
    messages = []
    inbox_dir = ROOT / "inbox"
    if not inbox_dir.exists():
        return messages
    for f in sorted(inbox_dir.glob("*.json")):
        try:
            data = json.loads(f.read_text())
        except Exception:
            continue
        if data.get("status") == "pending":
            data["_file"] = f.name
            messages.append(data)
    messages.sort(key=lambda m: m.get("received_at", ""), reverse=True)
    return messages


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

def render_inbox_cards(inbox):
    if not inbox:
        return '<div class="inbox-empty">All caught up — no pending messages.</div>'
    cards = ""
    for msg in inbox:
        msg_id   = msg.get("id", msg.get("_file", ""))
        channel  = msg.get("channel", "")
        ch_label = "WhatsApp" if channel == "whatsapp" else "Web form"
        ch_cls   = "channel-whatsapp" if channel == "whatsapp" else "channel-webform"
        from_name    = msg.get("from_name", "Unknown")
        from_contact = msg.get("from_contact", "")
        received     = msg.get("received_at", "")[:16].replace("T", " ")
        message      = msg.get("message", "").replace("<", "&lt;").replace(">", "&gt;")
        draft        = msg.get("draft", "").replace("<", "&lt;").replace(">", "&gt;")
        cards += f"""
    <div class="inbox-card" id="card-{msg_id}">
      <div class="inbox-card-header">
        <span class="channel-badge {ch_cls}">{ch_label}</span>
        <div class="inbox-from">
          {from_name}
          <span class="inbox-from-sub">{from_contact}</span>
        </div>
        <span class="inbox-time">{received}</span>
      </div>
      <div class="message-bubble">{message}</div>
      <div class="draft-label">Draft response</div>
      <textarea class="draft-textarea" id="draft-{msg_id}">{draft}</textarea>
      <div class="inbox-actions">
        <button class="btn-send" onclick="inboxAction('{msg_id}','send')">Approve &amp; Send</button>
        <button class="btn-dismiss" onclick="inboxAction('{msg_id}','dismiss')">Dismiss</button>
      </div>
    </div>"""
    return cards

def render_html(clients, appointments, finances, inbox):
    upcoming = [a for a in appointments if not a["past"]]
    active = [c for c in clients if c["active_order"]]
    leads  = [c for c in clients if not c["active_order"]]

    # Stats
    stat_orders = len(active)
    stat_leads  = len(leads)
    stat_appts  = len(upcoming)
    stat_inbox  = len(inbox)

    # Inbox
    inbox_html   = render_inbox_cards(inbox)
    inbox_badge  = f'<span class="wip" style="background:#FEE2E2;color:#DC2626">{stat_inbox}</span>' if stat_inbox else ""

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

  /* ── Inbox cards ── */
  .inbox-card {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 18px;
    margin-bottom: 12px;
  }}
  .inbox-card-header {{
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 12px;
  }}
  .channel-badge {{
    padding: 3px 10px;
    border-radius: 99px;
    font-size: 11px;
    font-weight: 600;
    color: white;
    flex-shrink: 0;
  }}
  .channel-whatsapp {{ background: #25D366; }}
  .channel-webform  {{ background: #3B82F6; }}
  .inbox-from {{ font-weight: 600; font-size: 14px; flex: 1; min-width: 0; }}
  .inbox-from-sub {{ font-size: 12px; color: var(--muted); display: block; font-weight: 400; }}
  .inbox-time {{ font-size: 11px; color: #A8A29E; flex-shrink: 0; }}
  .message-bubble {{
    background: #F5F5F4;
    border-radius: 12px;
    padding: 12px 14px;
    font-size: 13px;
    line-height: 1.5;
    color: var(--text);
    margin-bottom: 12px;
  }}
  .draft-label {{
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--muted);
    margin-bottom: 6px;
  }}
  .draft-textarea {{
    width: 100%;
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 10px 12px;
    font-size: 13px;
    font-family: inherit;
    color: var(--text);
    background: var(--bg);
    resize: vertical;
    min-height: 90px;
    margin-bottom: 10px;
    outline: none;
    transition: border-color 0.15s;
    box-sizing: border-box;
  }}
  .draft-textarea:focus {{ border-color: var(--accent); }}
  .inbox-actions {{ display: flex; gap: 8px; }}
  .btn-send {{
    background: var(--accent);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 8px 16px;
    font-size: 13px;
    font-weight: 500;
    cursor: pointer;
    transition: opacity 0.15s;
  }}
  .btn-send:hover {{ opacity: 0.85; }}
  .btn-dismiss {{
    background: none;
    color: var(--muted);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 8px 14px;
    font-size: 13px;
    cursor: pointer;
    transition: color 0.15s;
  }}
  .btn-dismiss:hover {{ color: var(--text); }}
  .inbox-empty {{
    text-align: center;
    padding: 48px 0;
    font-size: 14px;
    color: var(--muted);
  }}
  .header-link {{
    font-size: 12px;
    color: var(--muted);
    text-decoration: none;
    padding: 6px 10px;
    border: 1px solid var(--border);
    border-radius: 8px;
    transition: color 0.15s;
    white-space: nowrap;
  }}
  .header-link:hover {{ color: var(--text); }}

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
  <a href="/contact" class="header-link">Contact form ↗</a>
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
    <div class="stat-num">{stat_inbox}</div>
    <div class="stat-label">Inbox</div>
  </div>
</div>

<div class="tab-nav">
  <div class="tab active" data-panel="clients">Clients</div>
  <div class="tab" data-panel="appointments">Appointments</div>
  <div class="tab" data-panel="orders">Orders <span class="wip">soon</span></div>
  <div class="tab" data-panel="finances">Finances <span class="wip">soon</span></div>
  <div class="tab" data-panel="inbox">Inbox {inbox_badge}</div>
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
    {inbox_html}
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

  function inboxAction(id, action) {{
    fetch('/inbox/action', {{
      method: 'POST',
      headers: {{'Content-Type': 'application/json'}},
      body: JSON.stringify({{id, action}})
    }}).then(r => r.json()).then(data => {{
      if (data.ok) {{
        const card = document.getElementById('card-' + id);
        if (card) {{
          card.style.transition = 'opacity 0.3s';
          card.style.opacity = '0';
          setTimeout(() => {{
            card.remove();
            const panel = document.getElementById('panel-inbox');
            if (!panel.querySelector('.inbox-card')) {{
              panel.innerHTML = '<div class="inbox-empty">All caught up — no pending messages.</div>';
            }}
          }}, 300);
        }}
      }}
    }}).catch(() => alert('Action failed — please try again.'));
  }}
</script>
</body>
</html>"""


# ── HTTP server ───────────────────────────────────────────────────────────────

CONTACT_FORM_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Contact — Juliette by Julia Arnau</title>
<style>
  :root { --bg:#FAF8F5; --surface:#FFFFFF; --border:#EDE9E3; --text:#1C1917; --muted:#78716C; --accent:#9D7B5A; }
  * { box-sizing:border-box; margin:0; padding:0; }
  body { font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; background:var(--bg); color:var(--text); min-height:100vh; display:flex; flex-direction:column; align-items:center; padding:40px 20px; }
  .back { align-self:flex-start; font-size:13px; color:var(--muted); text-decoration:none; margin-bottom:32px; }
  .back:hover { color:var(--text); }
  .card { background:var(--surface); border:1px solid var(--border); border-radius:18px; padding:32px; width:100%; max-width:480px; }
  h1 { font-size:22px; font-weight:700; margin-bottom:4px; }
  .sub { font-size:14px; color:var(--muted); margin-bottom:28px; }
  label { display:block; font-size:12px; font-weight:600; text-transform:uppercase; letter-spacing:.06em; color:var(--muted); margin-bottom:6px; margin-top:18px; }
  input, textarea { width:100%; border:1px solid var(--border); border-radius:10px; padding:10px 12px; font-size:14px; font-family:inherit; color:var(--text); background:var(--bg); outline:none; transition:border-color .15s; }
  input:focus, textarea:focus { border-color:var(--accent); }
  textarea { min-height:110px; resize:vertical; }
  .opt { font-weight:400; color:#A8A29E; text-transform:none; letter-spacing:0; font-size:11px; }
  button { margin-top:24px; width:100%; background:var(--accent); color:#fff; border:none; border-radius:10px; padding:13px; font-size:15px; font-weight:600; cursor:pointer; transition:opacity .15s; }
  button:hover { opacity:.88; }
</style>
</head>
<body>
<a class="back" href="/">&#8592; Back to dashboard</a>
<div class="card">
  <h1>Get in touch</h1>
  <p class="sub">Tell us about your wedding and we'll be in touch soon.</p>
  <form method="POST" action="/contact">
    <label>Name</label>
    <input type="text" name="name" required placeholder="Your full name">
    <label>Email</label>
    <input type="email" name="email" required placeholder="you@example.com">
    <label>Phone <span class="opt">optional</span></label>
    <input type="tel" name="phone" placeholder="+34 600 000 000">
    <label>Wedding date <span class="opt">approximate is fine</span></label>
    <input type="text" name="wedding_date" placeholder="e.g. June 2027">
    <label>Message</label>
    <textarea name="message" required placeholder="Tell us about your vision, style, any inspiration..."></textarea>
    <button type="submit">Send message</button>
  </form>
</div>
</body>
</html>"""

CONTACT_THANKS_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Thank you — Juliette by Julia Arnau</title>
<style>
  :root { --bg:#FAF8F5; --surface:#FFFFFF; --border:#EDE9E3; --text:#1C1917; --muted:#78716C; --accent:#9D7B5A; }
  * { box-sizing:border-box; margin:0; padding:0; }
  body { font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; background:var(--bg); color:var(--text); min-height:100vh; display:flex; align-items:center; justify-content:center; padding:40px 20px; }
  .card { background:var(--surface); border:1px solid var(--border); border-radius:18px; padding:40px 32px; text-align:center; max-width:400px; width:100%; }
  .icon { font-size:40px; margin-bottom:20px; }
  h1 { font-size:22px; font-weight:700; margin-bottom:10px; }
  p { font-size:14px; color:var(--muted); line-height:1.6; margin-bottom:24px; }
  a { color:var(--accent); font-size:14px; text-decoration:none; }
</style>
</head>
<body>
<div class="card">
  <div class="icon">&#9825;</div>
  <h1>Thank you!</h1>
  <p>Your message has been received. We'll be in touch with you shortly.</p>
  <a href="/contact">&#8592; Send another message</a>
</div>
</body>
</html>"""


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/contact":
            self._send(200, "text/html", CONTACT_FORM_HTML)
            return
        clients = load_clients()
        appointments = load_appointments()
        finances = load_finances()
        inbox = load_inbox()
        html = render_html(clients, appointments, finances, inbox)
        self._send(200, "text/html", html)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)

        if self.path == "/inbox/action":
            try:
                data = json.loads(body)
                msg_id = data.get("id", "")
                action = data.get("action", "")
                inbox_dir = ROOT / "inbox"
                matched = None
                for f in inbox_dir.glob("*.json"):
                    try:
                        item = json.loads(f.read_text())
                    except Exception:
                        continue
                    if item.get("id") == msg_id or f.stem == msg_id:
                        item["status"] = "sent" if action == "send" else "dismissed"
                        f.write_text(json.dumps(item, ensure_ascii=False, indent=2))
                        matched = True
                        break
                self._send(200, "application/json", json.dumps({"ok": bool(matched)}))
            except Exception:
                self._send(400, "application/json", '{"ok":false}')

        elif self.path == "/contact":
            try:
                params = urllib.parse.parse_qs(body.decode("utf-8", errors="replace"))
                def p(k): return params.get(k, [""])[0].strip()
                ts = datetime.now().strftime("%Y-%m-%d-%H%M%S")
                entry = {
                    "id": f"{ts}-webform",
                    "channel": "webform",
                    "from_name": p("name"),
                    "from_contact": p("email") or p("phone"),
                    "client_slug": "",
                    "received_at": datetime.now().isoformat(timespec="seconds"),
                    "message": p("message"),
                    "wedding_date": p("wedding_date"),
                    "draft": "",
                    "status": "pending",
                }
                inbox_dir = ROOT / "inbox"
                inbox_dir.mkdir(exist_ok=True)
                (inbox_dir / f"{ts}-webform.json").write_text(
                    json.dumps(entry, ensure_ascii=False, indent=2)
                )
                self._send(200, "text/html", CONTACT_THANKS_HTML)
            except Exception:
                self._send(500, "text/html", "<h1>Error</h1>")
        else:
            self._send(404, "text/plain", "Not found")

    def _send(self, code, ctype, content):
        encoded = content.encode() if isinstance(content, str) else content
        self.send_response(code)
        self.send_header("Content-Type", f"{ctype}; charset=utf-8")
        self.end_headers()
        self.wfile.write(encoded)

    def log_message(self, fmt, *args):
        pass

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"Dashboard running → http://localhost:{port}")
    print("Reads live from atelier/ — just refresh to update.")
    print("Ctrl+C to stop.\n")
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()
