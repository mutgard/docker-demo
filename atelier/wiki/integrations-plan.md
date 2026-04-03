# Integrations Plan

## Overview

This document outlines the planned integrations for the Juliette by Julia Arnau operations system. The dashboard currently demonstrates the UI with mock data; this file describes the real backend when ready to implement.

---

## 1. WhatsApp (Meta Cloud API)

**How it works:**
1. Client sends WhatsApp message to the business number.
2. Meta's webhook POSTs the message to `POST /webhook/whatsapp` on the dashboard server.
3. Dashboard saves message to `atelier/inbox/{timestamp}-whatsapp.json`.
4. Claude reads client profile + order context and pre-fills a draft response.
5. Julia reviews draft in the Inbox tab and clicks "Approve & Send".
6. Dashboard calls Meta Cloud API to send the reply.

**What you need:**
- Meta Business account with a verified phone number
- WhatsApp Cloud API access (free tier available)
- A publicly accessible URL for the webhook (Railway gives this automatically)

**Webhook payload received:**
```json
{
  "from": "34612345678",
  "name": "Sofia Martínez",
  "message": "Hi, can we reschedule my fitting?"
}
```

---

## 2. Web Contact Form

**How it works:**
1. Embed a form on the website (or use a standalone page at `/contact`).
2. Form submits `POST /webhook/webform` with name, email, phone, message.
3. Dashboard saves to `atelier/inbox/{timestamp}-webform.json`.
4. Claude drafts a response based on availability and current order book.
5. Julia reviews and sends reply via email.

**Form fields:**
- Name (required)
- Email (required)
- Phone (optional)
- Wedding date (optional)
- Message (required)

**Embed snippet (for any website builder):**
```html
<iframe src="https://your-railway-url.up.railway.app/contact"
        style="width:100%;border:none;min-height:500px"></iframe>
```

---

## 3. Google Calendar

**How it works:**
1. Appointments created in `atelier/appointments/` are synced to Google Calendar.
2. When Julia adds/updates an appointment via the dashboard, it creates/updates the Google Calendar event.
3. Optionally: Google Calendar changes sync back (two-way).

**What you need:**
- Google Cloud project with Calendar API enabled
- Service account credentials (JSON key file)
- Share the target calendar with the service account email

**Key events to sync:**
- Initial consultations
- Fittings (toile, first, second, final)
- Pickups / deliveries

---

## 4. Draft Response Generation (Claude API)

**How it works:**
When a new message arrives, the backend calls the Claude API with:
- The incoming message
- The client's profile (if matched by phone/name)
- Their current order stage
- Upcoming appointments
- Atelier tone/style guidelines

The response is saved as `draft` in the inbox JSON file and displayed in the Inbox tab for review.

**Context passed to Claude:**
```
You are the assistant for Juliette by Julia Arnau, a bridal atelier.
A message has arrived. Reply warmly, concisely, and in the same language as the client.

Client: Sofia Martínez
Current stage: second-fitting
Next appointment: 2026-04-12 at 11:00
Outstanding balance: €1,800 (due at final fitting)

Message: "Hi, can we reschedule my fitting?"
```

---

## Implementation Order (when ready)

1. Web contact form (simplest — no external accounts needed)
2. Claude API draft generation (just needs an API key)
3. WhatsApp webhook (needs Meta Business account)
4. Google Calendar sync (needs Google Cloud project)
