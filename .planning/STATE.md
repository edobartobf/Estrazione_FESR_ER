---
milestone: "v1.1"
name: "Drive PDF + Cartella Settimanale"
status: planning
progress:
  phases_total: 2
  phases_done: 0
  tasks_total: 0
  tasks_done: 0
---

## Current Position

Phase: Not started (defining requirements)
Plan: —
Status: Defining requirements
Last activity: 2026-06-11 — Milestone v1.1 started

## Project Reference

See: .planning/PROJECT.md

## Accumulated Context

### Decisions
- buildpayload() e buildpageparams() già avevano i campi data — ora esposti via datada/dataa kwargs
- datesuffix() usa abbreviazioni mese italiane: gen/feb/mar/apr/mag/giu/lug/ago/set/ott/nov/dic
- Drive via OAuth2 refresh token (no Service Account — cambiato in v1.0 phase 3)
- Configurazione sensibile gestita interamente via GitHub Secrets
- DATA_DA / DATA_A in scraper.py come config vars (default None = nessun filtro)
- Env var override via applysecrets() (FESR_* prefix)
- drive_url.txt come interfaccia tra upload_drive.py e notify_email.py
- SCARICA_PDF / SCARICA_LINK_PDF hardcoded a False in scraper.py — NON esposti come env var (gap da colmare in v1.1)
- upload_drive.py carica flat in GDRIVE_FOLDER_ID senza creare sottocartelle (gap da colmare in v1.1)

### Blockers
(none)

### Secrets configurati in GitHub (da v1.0)
- GDRIVE_CLIENT_ID, GDRIVE_CLIENT_SECRET, GDRIVE_REFRESH_TOKEN — OAuth2 Drive
- GDRIVE_FOLDER_ID — ID cartella Drive root
- SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS
- EMAIL_RECIPIENTS — lista email separata da virgola
