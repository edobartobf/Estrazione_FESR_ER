---
phase: 03-drive-email
plan: 03
status: complete
completed: 2026-06-11
---

# Summary — Plan 03-03: workflow activation

## What was done

Updated `.github/workflows/fesr_scraper.yml`:

- pip install now includes `google-auth google-api-python-client`
- Phase 3 placeholder comments replaced with active steps:
  - "Carica su Google Drive": runs upload_drive.py, conditioned on `secrets.GDRIVE_SA_JSON != ''`
  - "Invia email di riepilogo": runs notify_email.py, conditioned on `secrets.SMTP_HOST != ''`
- Both steps pass their FESR_OUTPUT=data and respective secrets as env vars
- Comment updated to "Phase 3 — Drive Upload + Email Notification"

## Verification

YAML valid. google-auth present. upload_drive.py and notify_email.py referenced.
GDRIVE_SA_JSON and SMTP_HOST both present. No placeholder comments remaining.
