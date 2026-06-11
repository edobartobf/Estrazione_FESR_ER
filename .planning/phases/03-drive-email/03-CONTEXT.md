---
phase: 03-drive-email
status: planned
created: 2026-06-11
---

# Phase 3 Context — Drive Upload + Email Notification

## Goal

Al termine di ogni run automatizzato, gli output sono disponibili su Google Drive e i destinatari ricevono un riepilogo via email.

## Requirements in scope

- AUTO-03: Upload CSV/JSON + PDF su Google Drive via Service Account
- AUTO-04: Email SMTP con conteggio delibere, azioni trovate, link Drive; zero delibere → email con count=0

## Architecture

### upload_drive.py

Nuovo script standalone chiamato dal workflow dopo lo scraper.

- Legge GDRIVE_SA_JSON (JSON stringa) da env — se assente, stampa errore e exit(1)
- Legge GDRIVE_FOLDER_ID da env — se assente, exit(1)
- Legge FESR_OUTPUT (default "data") per sapere quale cartella caricare
- Usa google-auth + google-api-python-client per uploadare tutti i file in data/ (ricorsivo)
- Stampa il link della cartella Drive
- Scrive drive_url.txt con il link (per notify_email.py)

### notify_email.py

Nuovo script standalone chiamato dopo upload_drive.py.

- Legge SMTP_HOST, SMTP_PORT (default 587), SMTP_USER, SMTP_PASS, EMAIL_RECIPIENTS da env
  — se mancano, exit(1) con messaggio esplicito
- Legge drive_url.txt per il link Drive (fallback "N/D" se non esiste)
- Legge i CSV in data/ per contare le delibere e raccogliere le azioni
- Manda email plain text con: conteggio, azioni, link Drive
- Subject: "FESR Scraper — N delibere trovate"
- Funziona anche con count=0 (AUTO-04 compliance)
- Solo stdlib: smtplib, email.mime — nessun pacchetto aggiuntivo

### Workflow update (.github/workflows/fesr_scraper.yml)

- pip install aggiunge google-auth google-api-python-client
- Commenti Phase 3 rimossi e sostituiti con step attivi
- Step Drive: condizionato su secrets.GDRIVE_SA_JSON != '' per evitare errori in fork senza secrets
- Step Email: condizionato su secrets.SMTP_HOST != ''

## Decisions

| Decision | Rationale |
|----------|-----------|
| google-api-python-client per Drive | SDK ufficiale Google, stabile, Service Account integrato |
| smtplib stdlib per email | Nessun pacchetto aggiuntivo; STARTTLS su porta 587 standard |
| drive_url.txt come interfaccia tra i due script | Evita accoppiamento diretto; semplice e leggibile |
| exit(1) se secret mancante | Soddisfa AUTO-05: workflow fallisce con errore esplicito |
| Upload ricorsivo di data/ | Carica CSV/JSON + sottocartella pdf/ automaticamente |
| Condizione if: secrets.X != '' | Evita step failures in fork pubblici senza secrets configurati |

## Secrets required (GitHub repository settings)

| Secret | Contenuto |
|--------|-----------|
| GDRIVE_SA_JSON | Service Account JSON come stringa (cat sa.json) |
| GDRIVE_FOLDER_ID | ID cartella Drive (dall'URL della cartella) |
| SMTP_HOST | es. smtp.gmail.com |
| SMTP_PORT | es. 587 (opzionale, default 587) |
| SMTP_USER | indirizzo email mittente |
| SMTP_PASS | app password |
| EMAIL_RECIPIENTS | lista email separata da virgola |

## Files created/modified

- `upload_drive.py` — nuovo
- `notify_email.py` — nuovo
- `.github/workflows/fesr_scraper.yml` — attivazione step Phase 3
