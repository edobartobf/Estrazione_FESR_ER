---
phase: 02-github-actions
status: planned
created: 2026-06-11
---

# Phase 2 Context — GitHub Actions Skeleton

## Goal

Lo scraping settimanale parte automaticamente ogni lunedì e può essere lanciato manualmente con parametri custom, senza credenziali nel codice.

## Requirements in scope

- AUTO-01: cron ogni lunedì, auto-calcola range lun–dom settimana precedente
- AUTO-02: workflow_dispatch con keyword e date custom
- AUTO-05: configurazione sensibile solo via GitHub Secrets

## Approach

### env var overrides in scraper.py (Plan 02-01)

scraper.py legge valori da os.environ al momento del run. Il modello scelto:
- Env var FESR_KEYWORD sovrascrive KEYWORD
- Env var FESR_DATA_DA sovrascrive DATA_DA
- Env var FESR_DATA_A sovrascrive DATA_A
- Env var FESR_ANNI sovrascrive ANNI
- Env var FESR_OUTPUT sovrascrive CARTELLA_OUTPUT

Implementato in una funzione `applysecrets()` chiamata all'inizio di `main()`.
Se l'env var non è impostata, il modulo usa il valore della variabile di default (nessun breaking change).

Env var name convention: `FESR_` prefix per evitare collisioni.

### GitHub Actions workflow YAML (Plan 02-02)

File: `.github/workflows/fesr_scraper.yml`

Trigger:
- `schedule: cron: "0 6 * * 1"` — ogni lunedì alle 06:00 UTC
- `workflow_dispatch` con inputs: keyword (default FESR), data_da, data_a

Passi principali:
1. checkout
2. setup-python 3.11
3. pip install requests beautifulsoup4
4. **Compute date range** — Python inline: se data_da/data_a non sono forniti (cron), calcola lun–dom della settimana precedente; scrive FESR_DATA_DA e FESR_DATA_A in GITHUB_ENV
5. **Run scraper** — `python scraper.py` con FESR_KEYWORD, FESR_DATA_DA, FESR_DATA_A in env
6. Upload artifacts (data/) per ispezione manuale
7. Placeholder commentato per Phase 3: Drive upload + email

### Calcolo settimana precedente

```python
from datetime import date, timedelta
today = date.today()
last_monday = today - timedelta(days=today.weekday() + 7)
last_sunday = last_monday + timedelta(days=6)
```

weekday() ritorna 0=lunedì … 6=domenica. `today.weekday() + 7` porta sempre all'ultimo lunedì passato (7 giorni fa se oggi è lunedì, altrimenti di più).

## Decisions

| Decision | Rationale |
|----------|-----------|
| Env vars invece di argomenti CLI | Evita riscrivere l'entry point; pattern standard per Actions; backward-compatible |
| Calcolo date in Python inline (not bash) | Evita dipendenze da `date --date` (GNU) vs BSD; coerente con il formato DD/MM/YYYY |
| ubuntu-latest runner | Standard, nessun requisito speciale |
| actions/upload-artifact per output | Permette di ispezionare il CSV senza Drive (Phase 3) |
| Nessun requirements.txt nel workflow | Dipendenze minime (requests + bs4) installate inline; evita file aggiuntivo |

## Phase 3 placeholders

Il workflow includerà commenti `# Phase 3:` che indicano dove inserire:
- Upload su Google Drive (Service Account JSON via secret GDRIVE_SA_JSON)
- Invio email SMTP (SMTP_HOST, SMTP_USER, SMTP_PASS, EMAIL_RECIPIENTS via secrets)

Questo rende evidente dove Phase 3 si aggancia senza codice non funzionante.

## Files modified

- `scraper.py` — aggiunta funzione `applysecrets()`
- `.github/workflows/fesr_scraper.yml` — nuovo file
