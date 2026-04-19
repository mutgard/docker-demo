"""Run once: python3 seed.py — inserts prototype sample data."""
from database import create_db, engine
from models import Client, Fabric, Appointment, Payment
from sqlmodel import Session

SEED = [
    {
        "client": Client(name="Aina Puig", wedding_date="17 Mai 2026", days_until=28,
                         status="clienta", garment="Vestit a mida",
                         garment_style="Princesa modern", measurements_date="12 Mar 2026",
                         phone="+34 639 42 18 05", email="aina.puig@mail.cat",
                         notes="Vol escot en V profund. Ha de poder ballar."),
        "fabrics": [
            Fabric(name="Mikado seda marfil", use="Cos",    qty="3.2 m", price="€48/m", to_buy=True,  supplier="Gratacós"),
            Fabric(name="Tul francès",        use="Vel",    qty="2.5 m", price="€22/m", to_buy=True,  supplier="Ribes & Casals"),
            Fabric(name="Crepe georgette",    use="Folre",  qty="4.0 m", price="€18/m", to_buy=False, supplier="Gratacós"),
            Fabric(name="Puntilla Chantilly", use="Vora",   qty="1.2 m", price="€95/m", to_buy=False, supplier="Gratacós"),
        ],
        "appointments": [
            Appointment(label="Prova 1", value="22 Mar — feta"),
            Appointment(label="Prova 2", value="18 Abr — programada"),
            Appointment(label="Entrega", value="15 Mai"),
        ],
        "payments": [
            Payment(label="Paga i senyal", value="€500 · rebut"),
            Payment(label="Saldo",         value="€1.800 pendent"),
        ],
    },
    {
        "client": Client(name="Berta Soler", wedding_date="31 Mai 2026", days_until=42,
                         status="sense-paga", garment="Vestit + vel",
                         garment_style="Romàntic clàssic", measurements_date="Pendent",
                         phone="+34 612 88 31 04", email="berta.soler@gmail.com", notes=""),
        "fabrics": [],
        "appointments": [Appointment(label="Consulta", value="10 Abr — feta")],
        "payments": [Payment(label="Paga i senyal", value="Pendent")],
    },
    {
        "client": Client(name="Clara Ferrer", wedding_date="14 Jun 2026", days_until=56,
                         status="clienta", garment="Vestit princesa",
                         garment_style="Royal / estructura", measurements_date="05 Feb 2026",
                         phone="+34 651 20 47 89", email="clara.ferrer@mail.com", notes=""),
        "fabrics": [
            Fabric(name="Mikado seda marfil",  use="Faldilla",  qty="5.5 m", price="€48/m", to_buy=False, supplier="Gratacós"),
            Fabric(name="Organza de seda",     use="Volants",   qty="8.0 m", price="€32/m", to_buy=False, supplier="Gratacós"),
            Fabric(name="Tul de cotó",         use="Enagua",    qty="6.0 m", price="€12/m", to_buy=False, supplier="Ribes & Casals"),
            Fabric(name="Puntilla Chantilly",  use="Escot",     qty="0.8 m", price="€95/m", to_buy=False, supplier="Gratacós"),
            Fabric(name="Crepe georgette",     use="Folre cos", qty="3.0 m", price="€18/m", to_buy=False, supplier="Gratacós"),
            Fabric(name="Entretela fusible",   use="Estructura",qty="2.5 m", price="€8/m",  to_buy=False, supplier="Habilitació Marín"),
        ],
        "appointments": [
            Appointment(label="Prova 1", value="14 Mar — feta"),
            Appointment(label="Prova 2", value="25 Abr — programada"),
        ],
        "payments": [
            Payment(label="Paga i senyal", value="€800 · rebut"),
            Payment(label="Saldo",         value="€2.200 pendent"),
        ],
    },
    {
        "client": Client(name="Dolors Vidal", wedding_date="28 Jun 2026", days_until=70,
                         status="prospect", garment="Consulta inicial",
                         garment_style="Per decidir", measurements_date="No preses",
                         phone="+34 608 55 12 37", email="dolors.vidal@outlook.com",
                         notes="Porta imatges de Pinterest. No vol cotilla."),
        "fabrics": [],
        "appointments": [Appointment(label="Consulta", value="22 Abr — pendent")],
        "payments": [],
    },
    {
        "client": Client(name="Elena Roca", wedding_date="05 Jul 2026", days_until=77,
                         status="clienta", garment="Vestit bohemi",
                         garment_style="Fluix / natural", measurements_date="18 Mar 2026",
                         phone="+34 699 14 88 62", email="elena.roca@gmail.com", notes=""),
        "fabrics": [
            Fabric(name="Gasa de cotó",      use="Cos",     qty="3.8 m", price="€14/m", to_buy=False, supplier="Ribes & Casals"),
            Fabric(name="Puntilla italiana", use="Màniga",  qty="0.8 m", price="€78/m", to_buy=True,  supplier="Gratacós"),
            Fabric(name="Setí de seda",      use="Cinturó", qty="0.5 m", price="€36/m", to_buy=False, supplier="Gratacós"),
        ],
        "appointments": [Appointment(label="Prova 1", value="02 Mai — programada")],
        "payments": [
            Payment(label="Paga i senyal", value="€400 · rebut"),
            Payment(label="Saldo",         value="€1.100 pendent"),
        ],
    },
    {
        "client": Client(name="Fina Batlle", wedding_date="12 Set 2025", days_until=-220,
                         status="entregada", garment="Vestit sirena",
                         garment_style="Glamour / escot obert", measurements_date="10 Oct 2024",
                         phone="+34 634 77 23 91", email="fina.batlle@yahoo.es",
                         notes="Bottons de perla a l'esquena. Clienta molt satisfeta."),
        "fabrics": [
            Fabric(name="Crepe de seda", use="Cos",   qty="4.5 m", price="€55/m", to_buy=False, supplier="Gratacós"),
            Fabric(name="Tul elàstic",   use="Folre", qty="3.0 m", price="€16/m", to_buy=False, supplier="Ribes & Casals"),
        ],
        "appointments": [
            Appointment(label="Prova 1", value="15 Nov 2024"),
            Appointment(label="Prova 2", value="14 Des 2024"),
            Appointment(label="Entrega", value="28 Ago 2025 — feta"),
        ],
        "payments": [
            Payment(label="Paga i senyal", value="€600 · rebut"),
            Payment(label="Saldo",         value="€2.200 · rebut"),
        ],
    },
]

def run_seed(s: Session):
    for entry in SEED:
        c = entry["client"]
        s.add(c); s.commit(); s.refresh(c)
        for f in entry["fabrics"]:
            f.client_id = c.id; s.add(f)
        for a in entry["appointments"]:
            a.client_id = c.id; s.add(a)
        for p in entry["payments"]:
            p.client_id = c.id; s.add(p)
        s.commit()

if __name__ == "__main__":
    create_db()
    with Session(engine) as s:
        run_seed(s)
    print("Seeded OK")
