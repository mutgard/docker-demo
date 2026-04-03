# Atelier Wiki

Welcome to the knowledge base for the bridal atelier. This wiki is maintained by Claude and serves as the single source of truth for all operations.

## Structure

```
atelier/
  clients/          # One folder per client
    _index.md       # Master client list
    {name}/
      profile.md    # Contact, source, wedding info
      measurements.md
      orders/       # One file per order
      comms/        # Communication logs
  orders/
    _index.md       # All orders + status
  appointments/
    _index.md       # All appointments
  finances/
    _index.md       # Financial overview
    invoices/       # One file per invoice
  templates/        # Blank forms — do not edit directly
  wiki/             # This section
```

## Key Concepts

- **Client slug**: URL-safe version of client name (e.g. `maria-garcia`)
- **Order ID**: Format `ORD-YYYY-NNN` (e.g. `ORD-2026-001`)
- **Invoice ID**: Format `INV-YYYY-NNN` (e.g. `INV-2026-001`)
- **Appointment file**: Named `YYYY-MM-DD-{client-slug}.md`
- **Comms log**: Named `YYYY-MM-DD-{channel}.md` inside the client's `comms/` folder

## Pages

- [[workflows]] — Standard operating procedures for all processes
- [[clients/_index]] — All clients
- [[orders/_index]] — All orders
- [[appointments/_index]] — All appointments
- [[finances/_index]] — Financial overview

---
*Last updated: —*
