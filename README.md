# Dr. Aahana Gupta — Sports Physiotherapy Platform

Production-grade multi-page Django application with a patient portal, staff dashboard, Calendly integration, and payment verification workflow.

## Features

### Public website
- Home, Services, Plans, Payment (UPI QR), Booking (Calendly), Reviews

### Patient portal (`/portal/`)
- Dashboard, payments, rehab progress, session history, profile
- Open registration for anyone
- **Guest payment flow**: submit UPI proof without login — portal account created when staff verifies payment

### Staff dashboard (`/staff/`) — for non-technical users
- Overview with pending payments & upcoming bookings
- **Verify/reject payments** → auto-creates patient login + email/WhatsApp credentials
- View Calendly bookings (auto-synced via webhook)
- Manage patients, rehab programs, and week-by-week progress
- Add consultation records
- Notification log (email + WhatsApp)
- **Auto-advance weeks** button + daily cron command

### Integrations
- **Calendly webhook** → auto-creates bookings on `invitee.created`
- **Email notifications** on payment verify & new rehab weeks
- **WhatsApp** via Twilio (optional; logs wa.me link if not configured)

---

## Quick start (local)

```bash
cd sportsphysio
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py create_staff_user --email aahanaguptaphysio@gmail.com --password yourpassword --name "Dr. Aahana"
python manage.py runserver
```

| URL | Purpose |
|-----|---------|
| http://127.0.0.1:8000/ | Public website |
| http://127.0.0.1:8000/staff/ | Staff dashboard |
| http://127.0.0.1:8000/portal/ | Patient portal |
| http://127.0.0.1:8000/admin/ | Django admin (advanced) |

---

## Docker

```bash
docker compose up --build
```

App runs at http://localhost:8000

Create staff user inside container:
```bash
docker compose exec web python manage.py create_staff_user --email you@example.com --password secret --name "Dr. Aahana"
```

---

## Deployment — important: Netlify will NOT work

**Netlify hosts static sites and serverless functions only.** This is a full Django Python application with a database, file uploads, and webhooks — it **cannot run on Netlify**.

### Recommended free/low-cost hosts for testing

| Platform | Why |
|----------|-----|
| **[Render](https://render.com)** | Free tier, native Docker/Python support |
| **[Railway](https://railway.app)** | Easy Docker deploy from GitHub |
| **[Fly.io](https://fly.io)** | Docker-based, good for testing |
| **Any VPS + Docker** | Use included `Dockerfile` |

### GitHub → Render (example)

1. Push `sportsphysio/` to GitHub
2. Create a **Web Service** on Render
3. Environment: **Docker**
4. Set env vars from `.env.example`
5. Add persistent disk for `/app/media` and `/app/data` (SQLite) or use Render PostgreSQL

### Calendly webhook setup

1. In Calendly → Integrations → Webhooks, add:
   ```
   https://YOUR-DOMAIN/webhooks/calendly/
   ```
2. Subscribe to events: `invitee.created`, `invitee.canceled`
3. Copy signing key → `CALENDLY_WEBHOOK_SIGNING_KEY` in env

### Daily auto week advancement (cron)

Run daily on your server:
```bash
python manage.py advance_rehab_weeks
```

Or use Render/Railway cron job.

---

## Workflow summary

```
Patient books on Calendly
    → Webhook auto-creates Booking

Patient pays via UPI + submits screenshot (no login needed)
    → Payment status: Pending

Dr. Aahana opens Staff Dashboard → verifies payment
    → Patient login created (email + temp password)
    → Email + WhatsApp sent with portal link
    → Monthly rehab: Week 1 program auto-created + notified

Each week (auto or manual from staff dashboard)
    → New ProgressEntry + email/WhatsApp to patient
```

---

## Environment variables

See `.env.example` for full list. Key vars:

| Variable | Purpose |
|----------|---------|
| `SITE_URL` | Public URL for links in emails |
| `CALENDLY_WEBHOOK_SIGNING_KEY` | Verify Calendly webhooks |
| `EMAIL_*` | SMTP for production emails |
| `TWILIO_*` | WhatsApp notifications (optional) |

---

## Staff dashboard guide (for Dr. Aahana)

1. **Sign in** at `/accounts/login/` with your staff email
2. **Pending payments** appear on the overview — click **Review** → **Verify Payment**
3. Patient receives login details automatically
4. **Bookings** tab shows Calendly appointments
5. **Rehab Programs** → open a program → **Add Week** to publish next week's exercises
6. **Auto-advance weeks** runs the 7-day check for all active programs

---

## License

Proprietary — © Dr. Aahana Gupta (PT). All rights reserved.
