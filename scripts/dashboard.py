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

def _parse_eur(s):
    """Parse '€1,234.50' or '€1234' to float, return 0.0 on failure."""
    try:
        return float(re.sub(r"[€,\s]", "", s))
    except Exception:
        return 0.0

def load_finances():
    invoices = []
    inv_dir = ROOT / "finances" / "invoices"
    if not inv_dir.exists():
        return invoices
    for f in sorted(inv_dir.glob("*.md")):
        text = f.read_text()
        client_m = re.search(r"\[\[clients/(.+?)/", text)
        client = client_m.group(1).replace("-", " ").title() if client_m else ""
        # Total is in a table row: | **Total** | €3,200 |
        total_m = re.search(r"\|\s*\*\*Total\*\*\s*\|\s*€([\d,]+(?:\.\d+)?)\s*\|", text)
        total = float(total_m.group(1).replace(",", "")) if total_m else 0.0
        paid  = _parse_eur(field(text, "Total paid"))
        # Parse individual payment rows: | YYYY-MM-DD | method | €amount | notes |
        payments = []
        for row in re.finditer(
            r"\|\s*(\d{4}-\d{2}-\d{2})\s*\|\s*([^|]+?)\s*\|\s*€([\d,]+(?:\.\d+)?)\s*\|",
            text,
        ):
            payments.append({
                "date":   row.group(1),
                "method": row.group(2).strip(),
                "amount": float(row.group(3).replace(",", "")),
            })
        # Status checkboxes
        status = {
            "deposit": bool(re.search(r"\[x\]\s*Deposit", text, re.IGNORECASE)),
            "balance": bool(re.search(r"\[x\]\s*Balance", text, re.IGNORECASE)),
            "receipt": bool(re.search(r"\[x\]\s*Receipt", text, re.IGNORECASE)),
        }
        invoices.append({
            "id":           f.stem,
            "client":       client,
            "invoice_date": field(text, "Invoice date"),
            "due_date":     field(text, "Due date"),
            "total":        total,
            "paid":         paid,
            "outstanding":  total - paid,
            "payments":     payments,
            "status":       status,
        })
    return invoices

def load_expenses():
    expenses = []
    exp_dir = ROOT / "finances" / "expenses"
    if not exp_dir.exists():
        return expenses
    for f in sorted(exp_dir.glob("*.md")):
        if f.name.startswith("_"):
            continue
        text = f.read_text()
        deductible_raw = field(text, "Deductible").lower()
        expenses.append({
            "date":          field(text, "Date"),
            "category":      field(text, "Category").lower(),
            "description":   field(text, "Description"),
            "amount_ex_iva": _parse_eur(field(text, "Amount (ex-IVA)")),
            "iva_rate":      int(re.sub(r"[^\d]", "", field(text, "IVA rate") or "0") or 0),
            "iva_amount":    _parse_eur(field(text, "IVA amount")),
            "total":         _parse_eur(field(text, "Total")),
            "method":        field(text, "Payment method"),
            "supplier":      field(text, "Supplier"),
            "deductible":    deductible_raw == "yes",
        })
    return expenses

def quarter_for_date(date_str):
    """Return (year_str, quarter_int) for a YYYY-MM-DD string."""
    try:
        month = int(date_str[5:7])
        year  = date_str[:4]
        return year, (month - 1) // 3 + 1
    except Exception:
        return None, None

def tax_summary(invoices, expenses, year, quarter):
    """Compute IVA (Modelo 303) and IRPF (Modelo 130) for one quarter."""
    IVA_RATE = 0.21

    # Income: sum payments received in this quarter
    income_total = 0.0  # IVA-inclusive
    for inv in invoices:
        for pmt in inv["payments"]:
            y, q = quarter_for_date(pmt["date"])
            if y == str(year) and q == quarter:
                income_total += pmt["amount"]

    income_base       = income_total / (1 + IVA_RATE)
    iva_repercutido   = income_total - income_base

    # Expenses: sum deductible expenses in this quarter
    expenses_base    = 0.0
    iva_soportado    = 0.0
    for exp in expenses:
        y, q = quarter_for_date(exp["date"])
        if y == str(year) and q == quarter and exp["deductible"]:
            expenses_base += exp["amount_ex_iva"]
            iva_soportado += exp["iva_amount"]

    iva_a_pagar  = max(0.0, iva_repercutido - iva_soportado)
    net_income   = income_base - expenses_base
    irpf_a_pagar = max(0.0, net_income * 0.20)

    quarter_ends = {1: "03", 2: "06", 3: "09", 4: "12"}
    due_months   = {1: f"{year}-04-20", 2: f"{year}-07-20",
                    3: f"{year}-10-20", 4: f"{int(year)+1}-01-20"}

    return {
        "income_total":    income_total,
        "income_base":     income_base,
        "iva_repercutido": iva_repercutido,
        "expenses_base":   expenses_base,
        "iva_soportado":   iva_soportado,
        "iva_a_pagar":     iva_a_pagar,
        "net_income":      net_income,
        "irpf_a_pagar":    irpf_a_pagar,
        "due_date":        due_months[quarter],
    }

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

def load_scenarios():
    scenarios = []
    sc_dir = ROOT / "demo-scenarios"
    if not sc_dir.exists():
        return scenarios
    for f in sorted(sc_dir.glob("*.json")):
        try:
            scenarios.append(json.loads(f.read_text()))
        except Exception:
            continue
    return scenarios

def create_client_files(scenario):
    """Write client profile, comms log, and update _index.md from a demo scenario."""
    slug = scenario["client_slug"]
    brief = scenario.get("brief", {})
    messages = scenario.get("messages", [])
    today = str(date.today())

    client_dir = ROOT / "clients" / slug
    comms_dir = client_dir / "comms"
    comms_dir.mkdir(parents=True, exist_ok=True)

    nombre = brief.get("nombre", "Por identificar")
    boda = brief.get("boda", "")
    iso_date_m = re.search(r"(\d{4}-\d{2}-\d{2})", boda)
    boda_iso = iso_date_m.group(1) if iso_date_m else boda

    # ── Profile ──────────────────────────────────────────────────────────────
    profile_path = client_dir / "profile.md"
    if not profile_path.exists():
        notes = ", ".join(filter(None, [
            brief.get("estilo", ""),
            brief.get("silueta", ""),
            f"tejido: {brief.get('tejido', '')}" if brief.get("tejido") else "",
            brief.get("color", ""),
        ]))
        profile_path.write_text(
            f"# Client: {nombre}\n\n"
            "## Contact\n"
            "- **Phone:** \n"
            "- **Email:** \n"
            f"- **WhatsApp:** {brief.get('telefono', '')}\n"
            "- **Instagram:** \n"
            "- **Address:** \n\n"
            "## Source\n"
            "- **How did they find us:** WhatsApp\n"
            "- **Referred by:** \n\n"
            "## Personal\n"
            f"- **Wedding date:** {boda_iso}\n"
            f"- **Venue:** {brief.get('lugar', '')}\n"
            f"- **Budget:** {brief.get('presupuesto', '')}\n"
            f"- **Notes:** {notes}\n\n"
            "## Status\n"
            f"- **Client since:** {today}\n"
            "- **Active order:** no\n"
            "- **Tags:** lead, intake-demo\n\n"
            "---\n"
            f"*Created: {today}*\n"
            f"*Last updated: {today}*\n"
        )

    # ── Comms log ────────────────────────────────────────────────────────────
    comms_path = comms_dir / f"{today}-whatsapp.md"
    if not comms_path.exists():
        thread_lines = []
        for m in messages:
            speaker = "Julia" if m["from"] == "julia" else "Cliente"
            thread_lines.append(f"**{speaker} [{m['time']}]:** {m['text']}")
        thread_text = "\n\n".join(thread_lines)

        comms_path.write_text(
            f"# Communication: {today} — {nombre}\n\n"
            "## Details\n"
            f"- **Date:** {today}\n"
            f"- **Time:** {messages[0]['time'] if messages else ''}\n"
            "- **Channel:** whatsapp\n"
            "- **Direction:** inbound\n"
            f"- **Client:** [[clients/{slug}/profile]]\n\n"
            "## Summary\n\n"
            f"Primera toma de contacto por WhatsApp. {nombre} expresa interés en un vestido a medida.\n\n"
            f"{thread_text}\n\n"
            "## Action items\n"
            "- [ ] Confirmar disponibilidad para primera sesión\n"
            "- [ ] Revisar presupuesto y plazos\n\n"
            "## Follow-up required\n"
            "- **By whom:** Julia\n"
            "- **By when:** \n"
            "- **Done:** no\n\n"
            "---\n"
            f"*Created: {today}*\n"
        )

    # ── Update _index.md ─────────────────────────────────────────────────────
    index_path = ROOT / "clients" / "_index.md"
    index_text = index_path.read_text()
    if slug not in index_text:
        new_row = f"| [{nombre}]({slug}/profile.md) | {today} | WhatsApp | — |\n"
        updated = re.sub(
            r"(## Leads.*?)((?:\|[^\n]+\|\n)+)",
            lambda m: m.group(0) + new_row,
            index_text,
            flags=re.DOTALL,
        )
        index_path.write_text(updated)

    return True


# ── HTML ──────────────────────────────────────────────────────────────────────

CATEGORY_COLORS = {
    "fabric":       ("#FEF3C7", "#D97706"),
    "tools":        ("#DBEAFE", "#1D4ED8"),
    "studio":       ("#F3E8FF", "#7C3AED"),
    "marketing":    ("#FCE7F3", "#DB2777"),
    "professional": ("#D1FAE5", "#059669"),
    "other":        ("#F3F4F6", "#6B7280"),
}

def _fmt_eur(n):
    return f"€{n:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def _days_until(date_str):
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d").date()
        return (d - date.today()).days
    except Exception:
        return 999

def render_finances_html(invoices, expenses):
    today_year  = date.today().year
    today_month = date.today().month
    current_q   = (today_month - 1) // 3 + 1

    # ── YTD totals ────────────────────────────────────────────────────────────
    ytd_income = sum(
        pmt["amount"]
        for inv in invoices
        for pmt in inv["payments"]
        if pmt["date"][:4] == str(today_year)
    )
    ytd_income_base = ytd_income / 1.21
    ytd_expenses = sum(
        e["total"] for e in expenses if e["date"][:4] == str(today_year)
    )
    ytd_expenses_base = sum(
        e["amount_ex_iva"] for e in expenses if e["date"][:4] == str(today_year)
    )
    ytd_net = ytd_income_base - ytd_expenses_base
    outstanding = sum(inv["outstanding"] for inv in invoices)

    # ── Current quarter tax ───────────────────────────────────────────────────
    cur_tax = tax_summary(invoices, expenses, today_year, current_q)
    days_left = _days_until(cur_tax["due_date"])
    urgent = days_left <= 15

    # ── Summary strip ─────────────────────────────────────────────────────────
    summary_html = f"""
    <div class="fin-summary">
      <div class="fin-stat">
        <div class="fin-stat-num" style="color:#059669">{_fmt_eur(ytd_income_base)}</div>
        <div class="fin-stat-label">Ingresos netos {today_year}</div>
      </div>
      <div class="fin-stat">
        <div class="fin-stat-num" style="color:#DC2626">{_fmt_eur(ytd_expenses_base)}</div>
        <div class="fin-stat-label">Gastos netos {today_year}</div>
      </div>
      <div class="fin-stat">
        <div class="fin-stat-num">{_fmt_eur(ytd_net)}</div>
        <div class="fin-stat-label">Resultado neto</div>
      </div>
      <div class="fin-stat">
        <div class="fin-stat-num" style="color:#D97706">{_fmt_eur(outstanding)}</div>
        <div class="fin-stat-label">Pendiente cobro</div>
      </div>
    </div>"""

    # ── Tax alert box ─────────────────────────────────────────────────────────
    q_labels = {1: "T1 (ene–mar)", 2: "T2 (abr–jun)", 3: "T3 (jul–sep)", 4: "T4 (oct–dic)"}
    urgent_cls = " urgent" if urgent else ""
    days_msg = (
        f'<span style="color:#DC2626;font-weight:600">Vence en {days_left} días</span>'
        if urgent
        else f"Vence el {cur_tax['due_date']}"
    )
    tax_html = f"""
    <div class="tax-box{urgent_cls}">
      <div class="tax-box-header">
        <span class="tax-q-label">{q_labels[current_q]} — Impuestos estimados</span>
        <span class="tax-due">{days_msg}</span>
      </div>
      <div class="tax-grid">
        <div class="tax-item">
          <div class="tax-model">Modelo 303</div>
          <div class="tax-name">IVA a ingresar</div>
          <div class="tax-amount">{_fmt_eur(cur_tax['iva_a_pagar'])}</div>
          <div class="tax-detail">Repercutido {_fmt_eur(cur_tax['iva_repercutido'])} − Soportado {_fmt_eur(cur_tax['iva_soportado'])}</div>
        </div>
        <div class="tax-item">
          <div class="tax-model">Modelo 130</div>
          <div class="tax-name">IRPF a ingresar</div>
          <div class="tax-amount">{_fmt_eur(cur_tax['irpf_a_pagar'])}</div>
          <div class="tax-detail">20% sobre rendimiento neto {_fmt_eur(cur_tax['net_income'])}</div>
        </div>
        <div class="tax-item">
          <div class="tax-model">Base</div>
          <div class="tax-name">Ingresos cobrados</div>
          <div class="tax-amount">{_fmt_eur(cur_tax['income_base'])}</div>
          <div class="tax-detail">IVA incluido: {_fmt_eur(cur_tax['income_total'])}</div>
        </div>
        <div class="tax-item">
          <div class="tax-model">Gastos</div>
          <div class="tax-name">Gastos deducibles</div>
          <div class="tax-amount">{_fmt_eur(cur_tax['expenses_base'])}</div>
          <div class="tax-detail">IVA soportado: {_fmt_eur(cur_tax['iva_soportado'])}</div>
        </div>
      </div>
    </div>"""

    # ── Quarterly breakdown ────────────────────────────────────────────────────
    q_rows = ""
    for q in range(1, 5):
        qt = tax_summary(invoices, expenses, today_year, q)
        dim = "" if q <= current_q else ' style="opacity:.45"'
        q_rows += f"""
        <tr{dim}>
          <td>{q_labels[q]}</td>
          <td class="num">{_fmt_eur(qt['income_base'])}</td>
          <td class="num">{_fmt_eur(qt['expenses_base'])}</td>
          <td class="num">{_fmt_eur(qt['net_income'])}</td>
          <td class="num">{_fmt_eur(qt['iva_a_pagar'])}</td>
          <td class="num">{_fmt_eur(qt['irpf_a_pagar'])}</td>
        </tr>"""

    quarterly_html = f"""
    <h2 class="section-label" style="margin-top:28px">Resumen trimestral {today_year}</h2>
    <div class="table-wrap">
      <table class="finance-table">
        <thead>
          <tr>
            <th>Trimestre</th>
            <th class="num">Ingresos</th>
            <th class="num">Gastos</th>
            <th class="num">Resultado</th>
            <th class="num">IVA 303</th>
            <th class="num">IRPF 130</th>
          </tr>
        </thead>
        <tbody>{q_rows}</tbody>
      </table>
    </div>"""

    # ── Monthly bar chart ─────────────────────────────────────────────────────
    monthly_income = {}
    for inv in invoices:
        for pmt in inv["payments"]:
            if pmt["date"][:4] == str(today_year):
                month_key = pmt["date"][:7]
                monthly_income[month_key] = monthly_income.get(month_key, 0) + pmt["amount"] / 1.21
    monthly_expenses = {}
    for e in expenses:
        if e["date"][:4] == str(today_year):
            month_key = e["date"][:7]
            monthly_expenses[month_key] = monthly_expenses.get(month_key, 0) + e["amount_ex_iva"]

    all_months = sorted(set(list(monthly_income.keys()) + list(monthly_expenses.keys())))
    max_val = max([monthly_income.get(m, 0) for m in all_months] + [1])
    month_names = {"01":"Ene","02":"Feb","03":"Mar","04":"Abr","05":"May","06":"Jun",
                   "07":"Jul","08":"Ago","09":"Sep","10":"Oct","11":"Nov","12":"Dic"}

    bars_html = ""
    for m in all_months:
        inc  = monthly_income.get(m, 0)
        exp  = monthly_expenses.get(m, 0)
        ih   = max(4, int(inc / max_val * 120))
        eh   = max(0, int(exp / max_val * 120))
        label = month_names.get(m[5:7], m[5:7])
        bars_html += f"""
      <div class="bar-group">
        <div class="bar-pair">
          <div class="bar bar-income" style="height:{ih}px" title="Ingresos {_fmt_eur(inc)}"></div>
          <div class="bar bar-expense" style="height:{eh}px" title="Gastos {_fmt_eur(exp)}"></div>
        </div>
        <div class="bar-label">{label}</div>
      </div>"""

    chart_legend = """
    <div class="chart-legend">
      <span class="legend-dot" style="background:#059669"></span> Ingresos
      <span class="legend-dot" style="background:#DC2626;margin-left:14px"></span> Gastos
    </div>"""

    chart_html = f"""
    <h2 class="section-label" style="margin-top:28px">Evolución mensual {today_year}</h2>
    {chart_legend}
    <div class="bar-chart">{bars_html}</div>"""  if all_months else ""

    # ── Invoices table ────────────────────────────────────────────────────────
    inv_rows = ""
    for inv in invoices:
        dep_dot = '<span class="status-dot paid">●</span>' if inv["status"]["deposit"] else '<span class="status-dot unpaid">●</span>'
        bal_dot = '<span class="status-dot paid">●</span>' if inv["status"]["balance"] else '<span class="status-dot unpaid">●</span>'
        inv_rows += f"""
        <tr>
          <td>{inv['id']}</td>
          <td>{inv['client']}</td>
          <td class="num">{_fmt_eur(inv['total'])}</td>
          <td class="num">{_fmt_eur(inv['paid'])}</td>
          <td class="num" style="{'color:#DC2626;font-weight:600' if inv['outstanding'] > 0 else ''}">{_fmt_eur(inv['outstanding'])}</td>
          <td class="center">{dep_dot} Dep &nbsp; {bal_dot} Sal</td>
          <td>{inv['due_date']}</td>
        </tr>"""

    invoices_html = f"""
    <h2 class="section-label" style="margin-top:28px">Facturas</h2>
    <div class="table-wrap">
      <table class="finance-table">
        <thead>
          <tr>
            <th>Factura</th>
            <th>Cliente</th>
            <th class="num">Total</th>
            <th class="num">Cobrado</th>
            <th class="num">Pendiente</th>
            <th class="center">Estado</th>
            <th>Vencimiento</th>
          </tr>
        </thead>
        <tbody>{inv_rows}</tbody>
      </table>
    </div>""" if invoices else ""

    # ── Expenses table ────────────────────────────────────────────────────────
    exp_rows = ""
    for e in expenses:
        bg, fg = CATEGORY_COLORS.get(e["category"], ("#F3F4F6", "#6B7280"))
        pill = f'<span class="category-pill" style="background:{bg};color:{fg}">{e["category"]}</span>'
        exp_rows += f"""
        <tr>
          <td>{e['date']}</td>
          <td>{pill}</td>
          <td>{e['description']}</td>
          <td>{e['supplier']}</td>
          <td class="num">{_fmt_eur(e['amount_ex_iva'])}</td>
          <td class="num">{_fmt_eur(e['iva_amount'])}</td>
          <td class="num"><strong>{_fmt_eur(e['total'])}</strong></td>
        </tr>"""

    expenses_html = f"""
    <h2 class="section-label" style="margin-top:28px">Gastos</h2>
    <div class="table-wrap">
      <table class="finance-table">
        <thead>
          <tr>
            <th>Fecha</th>
            <th>Categoría</th>
            <th>Descripción</th>
            <th>Proveedor</th>
            <th class="num">Base</th>
            <th class="num">IVA</th>
            <th class="num">Total</th>
          </tr>
        </thead>
        <tbody>{exp_rows}</tbody>
      </table>
    </div>""" if expenses else ""

    return summary_html + tax_html + quarterly_html + chart_html + invoices_html + expenses_html


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

def render_intake_html(scenarios):
    if not scenarios:
        return '<div class="empty">No demo scenarios found in atelier/demo-scenarios/</div>'

    options_html = "\n".join(
        f'      <option value="{s["id"]}">{s["label"]}</option>'
        for s in scenarios
    )
    scenarios_json = json.dumps(
        {s["id"]: s for s in scenarios}, ensure_ascii=False, indent=2
    )

    return f"""
<div style="display:flex;align-items:center;gap:16px;margin-bottom:28px;flex-wrap:wrap">
  <span style="font-size:11px;letter-spacing:2px;color:var(--muted);text-transform:uppercase;flex-shrink:0">Demo scenario</span>
  <select id="scenario-select"
    style="font-family:inherit;font-size:13px;padding:8px 12px;border:1px solid var(--border);
           border-radius:2px;background:var(--surface);color:var(--text);cursor:pointer;min-width:240px"
    onchange="loadScenario(this.value)">
{options_html}
  </select>
  <span id="intake-status" style="font-size:12px;color:var(--muted);margin-left:auto"></span>
</div>

<div id="intake-grid" style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:20px;align-items:start">
  <div id="col-thread"></div>
  <div id="col-brief"></div>
  <div id="col-action"></div>
</div>

<script>
const SCENARIOS = {scenarios_json};

function renderThread(sc) {{
  const msgs = (sc.messages || []).map(m => {{
    const isJulia = m.from === 'julia';
    const bg = isJulia ? '#F5EFE8' : '#EBF5F0';
    const align = isJulia ? 'flex-start' : 'flex-end';
    const label = isJulia ? 'Julia \U0001F90D' : 'Cliente';
    return `<div style="display:flex;flex-direction:column;align-items:${{align}};margin-bottom:12px">
      <div style="font-size:10px;color:#78716C;margin-bottom:3px;letter-spacing:0.5px">${{label}} \xb7 ${{m.time}}</div>
      <div style="background:${{bg}};padding:10px 14px;border-radius:12px;max-width:82%;font-size:13px;line-height:1.5;color:#1C1917">${{m.text}}</div>
    </div>`;
  }}).join('');

  document.getElementById('col-thread').innerHTML = `
    <div style="font-size:10px;letter-spacing:2px;color:var(--accent);font-weight:600;margin-bottom:12px;text-transform:uppercase">Conversaci\xf3n WhatsApp</div>
    <div style="background:#fff;border:1px solid var(--border);border-radius:4px;padding:16px;min-height:300px">
      <div style="display:flex;align-items:center;gap:8px;padding-bottom:12px;margin-bottom:12px;border-bottom:1px solid var(--border)">
        <div style="width:32px;height:32px;border-radius:50%;background:var(--accent-light);display:flex;align-items:center;justify-content:center;font-size:16px">\U0001F90D</div>
        <div>
          <div style="font-size:13px;font-weight:600;color:var(--text)">Julia \xb7 Atelier</div>
          <div style="font-size:11px;color:var(--muted)">WhatsApp</div>
        </div>
      </div>
      ${{msgs}}
    </div>`;
}}

function renderBrief(sc) {{
  const b = sc.brief || {{}};
  const fields = [
    ['Nombre', b.nombre], ['Boda', b.boda], ['Lugar', b.lugar],
    ['Estilo', b.estilo], ['Silueta', b.silueta], ['Escote', b.escote],
    ['Tejido', b.tejido], ['Cola', b.cola], ['Color', b.color],
    ['Presupuesto', b.presupuesto],
  ].filter(([, v]) => v).map(([k, v]) =>
    `<div style="display:flex;gap:8px;padding:8px 0;border-bottom:1px solid var(--border);font-size:13px">
      <span style="color:var(--muted);min-width:90px;flex-shrink:0">${{k}}</span>
      <span style="color:var(--text)">${{v}}</span>
    </div>`
  ).join('');

  const alerts = (b.alertas || []).map(a =>
    `<div style="background:#FEF3C7;border-left:3px solid #D97706;padding:8px 12px;font-size:12px;color:#92400E;margin-top:8px;border-radius:2px">\u26a0 ${{a}}</div>`
  ).join('');

  document.getElementById('col-brief').innerHTML = `
    <div style="font-size:10px;letter-spacing:2px;color:var(--accent);font-weight:600;margin-bottom:12px;text-transform:uppercase">Brief extra\xeddo</div>
    <div style="background:#fff;border:1px solid var(--border);border-radius:4px;padding:16px">
      ${{fields}}
      ${{alerts}}
    </div>`;
}}

function renderAction(sc) {{
  const b = sc.brief || {{}};
  document.getElementById('col-action').innerHTML = `
    <div style="font-size:10px;letter-spacing:2px;color:var(--accent);font-weight:600;margin-bottom:12px;text-transform:uppercase">Nueva clienta</div>
    <div style="background:#fff;border:1px solid var(--border);border-radius:4px;padding:20px">
      <div style="font-family:Georgia,serif;font-size:18px;color:var(--text);margin-bottom:4px">${{b.nombre || '\u2014'}}</div>
      <div style="font-size:12px;color:var(--muted);margin-bottom:16px">${{b.boda || ''}}</div>
      <div style="display:flex;flex-direction:column;gap:6px;margin-bottom:20px;font-size:13px">
        <div><span style="color:var(--muted)">Estilo: </span>${{b.estilo || '\u2014'}}</div>
        <div><span style="color:var(--muted)">Presupuesto: </span>${{b.presupuesto || '\u2014'}}</div>
      </div>
      <button id="create-btn"
        onclick="createClient('${{sc.id}}')"
        style="width:100%;padding:12px;background:var(--accent);color:#fff;border:none;border-radius:2px;
               font-family:inherit;font-size:13px;letter-spacing:1px;cursor:pointer;text-transform:uppercase">
        Crear ficha de clienta
      </button>
      <div id="create-result" style="margin-top:12px;font-size:12px;color:var(--muted);text-align:center"></div>
    </div>`;
}}

function loadScenario(id) {{
  const sc = SCENARIOS[id];
  if (!sc) return;
  const r = document.getElementById('create-result');
  if (r) r.textContent = '';
  renderThread(sc);
  renderBrief(sc);
  renderAction(sc);
}}

function createClient(scenarioId) {{
  const btn = document.getElementById('create-btn');
  const result = document.getElementById('create-result');
  btn.disabled = true;
  btn.textContent = 'Creando...';
  fetch('/api/create-client', {{
    method: 'POST',
    headers: {{'Content-Type': 'application/json'}},
    body: JSON.stringify({{scenario_id: scenarioId}})
  }})
  .then(r => r.json())
  .then(data => {{
    if (data.ok) {{
      btn.textContent = '\u2713 Ficha creada';
      btn.style.background = '#3A8A5C';
      result.style.color = '#3A8A5C';
      result.textContent = 'Clienta a\xf1adida \u2192 ve a la pesta\xf1a Clients';
    }} else {{
      btn.disabled = false;
      btn.textContent = 'Crear ficha de clienta';
      result.style.color = '#DC2626';
      result.textContent = data.error || 'Error al crear ficha';
    }}
  }})
  .catch(() => {{
    btn.disabled = false;
    btn.textContent = 'Crear ficha de clienta';
    result.style.color = '#DC2626';
    result.textContent = 'Error de conexi\xf3n';
  }});
}}

// Initialise with first scenario
loadScenario(Object.keys(SCENARIOS)[0]);
</script>"""


def render_html(clients, appointments, finances, expenses, inbox, scenarios=None):
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

    # Finances
    finances_html = render_finances_html(finances, expenses)
    intake_html = render_intake_html(scenarios or [])

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

  /* ── Finances ── */
  .fin-summary {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
    gap: 12px;
    margin-bottom: 20px;
  }}
  .fin-stat {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 14px 16px;
  }}
  .fin-stat-num {{
    font-size: 20px;
    font-weight: 700;
    color: var(--text);
    line-height: 1.2;
  }}
  .fin-stat-label {{
    font-size: 11px;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: .06em;
    margin-top: 4px;
  }}
  .tax-box {{
    background: var(--surface);
    border: 1.5px solid var(--border);
    border-radius: 14px;
    padding: 18px;
    margin-bottom: 4px;
  }}
  .tax-box.urgent {{
    border-color: #FCA5A5;
    background: #FFF5F5;
  }}
  .tax-box-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 14px;
    flex-wrap: wrap;
    gap: 6px;
  }}
  .tax-q-label {{
    font-size: 13px;
    font-weight: 600;
    color: var(--text);
  }}
  .tax-due {{
    font-size: 12px;
    color: var(--muted);
  }}
  .tax-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
    gap: 12px;
  }}
  .tax-item {{
    background: var(--bg);
    border-radius: 10px;
    padding: 12px 14px;
  }}
  .tax-model {{
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: .07em;
    color: var(--muted);
    margin-bottom: 2px;
  }}
  .tax-name {{
    font-size: 12px;
    color: var(--muted);
    margin-bottom: 4px;
  }}
  .tax-amount {{
    font-size: 18px;
    font-weight: 700;
    color: var(--text);
  }}
  .tax-detail {{
    font-size: 10px;
    color: #A8A29E;
    margin-top: 3px;
    line-height: 1.4;
  }}
  .table-wrap {{
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
    border-radius: 12px;
    border: 1px solid var(--border);
    margin-bottom: 4px;
  }}
  .finance-table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
    background: var(--surface);
    border-radius: 12px;
    overflow: hidden;
  }}
  .finance-table th {{
    padding: 10px 14px;
    text-align: left;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: .06em;
    color: var(--muted);
    background: var(--bg);
    border-bottom: 1px solid var(--border);
    white-space: nowrap;
  }}
  .finance-table td {{
    padding: 10px 14px;
    border-bottom: 1px solid var(--border);
    color: var(--text);
    white-space: nowrap;
  }}
  .finance-table tbody tr:last-child td {{ border-bottom: none; }}
  .finance-table tbody tr:hover td {{ background: var(--bg); }}
  .finance-table .num {{ text-align: right; font-variant-numeric: tabular-nums; }}
  .finance-table .center {{ text-align: center; }}
  .category-pill {{
    display: inline-block;
    padding: 2px 9px;
    border-radius: 99px;
    font-size: 11px;
    font-weight: 500;
  }}
  .status-dot {{ font-size: 10px; }}
  .status-dot.paid  {{ color: #059669; }}
  .status-dot.unpaid {{ color: #D1D5DB; }}
  .bar-chart {{
    display: flex;
    align-items: flex-end;
    gap: 8px;
    padding: 12px 4px 0;
    overflow-x: auto;
    scrollbar-width: none;
    margin-bottom: 4px;
  }}
  .bar-chart::-webkit-scrollbar {{ display: none; }}
  .bar-group {{
    display: flex;
    flex-direction: column;
    align-items: center;
    flex-shrink: 0;
  }}
  .bar-pair {{
    display: flex;
    align-items: flex-end;
    gap: 2px;
    height: 128px;
  }}
  .bar {{
    width: 16px;
    border-radius: 4px 4px 0 0;
    min-height: 4px;
    cursor: default;
    transition: opacity .15s;
  }}
  .bar:hover {{ opacity: .75; }}
  .bar-income  {{ background: #059669; }}
  .bar-expense {{ background: #FCA5A5; }}
  .bar-label {{
    font-size: 10px;
    color: var(--muted);
    margin-top: 6px;
    text-align: center;
  }}
  .chart-legend {{
    font-size: 12px;
    color: var(--muted);
    margin-bottom: 6px;
    display: flex;
    align-items: center;
    gap: 4px;
  }}
  .legend-dot {{
    display: inline-block;
    width: 10px;
    height: 10px;
    border-radius: 2px;
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
  <div class="tab" data-panel="finances">Finances</div>
  <div class="tab" data-panel="inbox">Inbox {inbox_badge}</div>
  <div class="tab" data-panel="intake">Intake Demo ✦</div>
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
    {finances_html}
  </div>

  <div class="panel" id="panel-inbox">
    {inbox_html}
  </div>

  <div class="panel" id="panel-intake">
    {intake_html}
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
        expenses = load_expenses()
        inbox = load_inbox()
        scenarios = load_scenarios()
        html = render_html(clients, appointments, finances, expenses, inbox, scenarios)
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

        elif self.path == "/api/create-client":
            try:
                data = json.loads(body)
                scenario_id = data.get("scenario_id", "")
                scenarios = load_scenarios()
                scenario = next((s for s in scenarios if s["id"] == scenario_id), None)
                if not scenario:
                    self._send(404, "application/json",
                               json.dumps({"ok": False, "error": "Scenario not found"}))
                    return
                create_client_files(scenario)
                self._send(200, "application/json", json.dumps({"ok": True}))
            except Exception as e:
                self._send(500, "application/json",
                           json.dumps({"ok": False, "error": str(e)}))

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
