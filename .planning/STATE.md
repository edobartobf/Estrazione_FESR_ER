---
gsd_state_version: 1.0
milestone: v1.1
milestone_name: milestone
status: complete
last_updated: "2026-06-11T14:30:00.000Z"
last_activity: 2026-06-11 — Completed 05-01-PLAN.md
progress:
  total_phases: 2
  completed_phases: 2
  total_plans: 3
  completed_plans: 3
  percent: 100
---

## Current Position

Phase: 05-drive-subfolder-upload
Plan: 05-01 (COMPLETE)
Status: Milestone v1.1 complete — all phases done (PDF-01, DRIVE-01, DRIVE-02 satisfied)
Last activity: 2026-06-11 — Completed 05-01-PLAN.md

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
- SCARICA_PDF / SCARICA_LINK_PDF esposti come env var FESR_SCARICA_PDF / FESR_SCARICA_LINK_PDF in applysecrets() — bool parsing via ("true","1","yes"); implicazione prerequisito: SCARICA_PDF=True forza SCARICA_LINK_PDF=True (04-01)
- FESR_SCARICA_LINK_PDF: "true" e FESR_SCARICA_PDF: "true" hardcoded nel passo Esegui scraper di fesr_scraper.yml — download PDF abilitato in ogni run automatico (04-02)
- upload_drive.py ora crea sottocartella datata (FESR_{datesuffix}) in GDRIVE_FOLDER_ID e carica tutti i file al suo interno; drive_url.txt punta alla sottocartella
- datesuffix() duplicato inline in upload_drive.py (nessun import da scraper.py) per mantenere gli script indipendenti
- Service OAuth2 costruito una sola volta in main() e passato a create_subfolder() e upload_to_subfolder()

### Blockers

(none)

### Secrets configurati in GitHub (da v1.0)

- GDRIVE_CLIENT_ID, GDRIVE_CLIENT_SECRET, GDRIVE_REFRESH_TOKEN — OAuth2 Drive
- GDRIVE_FOLDER_ID — ID cartella Drive root
- SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS
- EMAIL_RECIPIENTS — lista email separata da virgola
