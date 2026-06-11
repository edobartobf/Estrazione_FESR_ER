---
milestone: "v1.0"
name: "Filtro per periodo + Automazione settimanale"
status: complete
progress:
  phases_total: 3
  phases_done: 3
  tasks_total: 0
  tasks_done: 0
---

## Current Position

All phases complete. Milestone v1.0 ready for audit and archiving.
Last activity: 2026-06-11 — Phase 3 executed (plans 03-01, 03-02, 03-03 complete)

## Project Reference

See: .planning/PROJECT.md

## Accumulated Context

### Decisions
- buildpayload() e buildpageparams() già avevano i campi data — ora esposti via datada/dataa kwargs
- datesuffix() usa abbreviazioni mese italiane: gen/feb/mar/apr/mag/giu/lug/ago/set/ott/nov/dic
- Drive via Service Account GCP (no OAuth interattivo in CI/CD)
- Configurazione sensibile gestita interamente via GitHub Secrets
- DATA_DA / DATA_A in scraper.py come config vars (default None = nessun filtro)
- Env var override via applysecrets() (FESR_* prefix)
- drive_url.txt come interfaccia tra upload_drive.py e notify_email.py

### Blockers
(none)

### Secrets to configure in GitHub (before first run)
- GDRIVE_SA_JSON — Service Account JSON (cat sa.json)
- GDRIVE_FOLDER_ID — ID cartella Drive
- SMTP_HOST, SMTP_PORT (opzionale), SMTP_USER, SMTP_PASS
- EMAIL_RECIPIENTS — lista email separata da virgola
