---
phase: 03-drive-email
plan: 02
status: complete
completed: 2026-06-11
---

# Summary — Plan 03-02: notify_email.py

## What was done

Created `notify_email.py` (stdlib only — smtplib, email.mime):

- `build_summary(output_folder)` — reads all `delibere_*.csv` in the folder, aggregates row count
  and unique semicolon-split azioni; returns {"count": int, "azioni": []}
- `send_email(...)` — SMTP with STARTTLS, MIMEMultipart message
- `main()` — validates SMTP_HOST, SMTP_USER, SMTP_PASS, EMAIL_RECIPIENTS (exit 1 if any missing),
  reads drive_url.txt for Drive link (fallback "N/D"), builds and sends email
- Subject: "FESR Scraper — N delibere trovate"
- Zero delibere → email sent with count=0 (AUTO-04 compliance)

## Verification

Automated checks passed: Task 1 OK.
Missing SMTP_HOST → exit 1, "SMTP_HOST" in stderr.
build_summary empty folder → count=0, azioni=[].
build_summary with CSV → correct count and azioni aggregation.
