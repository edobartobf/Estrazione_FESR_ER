# Estrazione FESR ER

## What This Is

Scraper Python che scarica le deliberazioni della giunta regionale dell'Emilia-Romagna dal portale SIIR, filtra per keyword (default "FESR") e produce file CSV/JSON strutturati con download opzionale dei PDF allegati.
Usato da analisti per monitorare le delibere FESR 2021-2027 senza accesso manuale al portale.

## Core Value

Estrarre tutte le delibere FESR di un periodo in modo affidabile e senza intervento manuale, con output pronti all'analisi.

## Current Milestone: v1.1 — Drive PDF + Cartella Settimanale

**Goal:** Caricare i PDF delle delibere su Google Drive insieme al CSV riassuntivo, organizzati in una sottocartella denominata con il periodo di riferimento.

**Target features:**
- Download PDF abilitato nell'automazione settimanale (SCARICA_PDF + SCARICA_LINK_PDF via env var)
- Creazione sottocartella Drive per ogni run con nome che riflette il periodo (es. `FESR_2026_W23`)
- Upload PDF + CSV riassuntivo nella sottocartella, non flat in GDRIVE_FOLDER_ID

## Requirements

### Validated

- ✓ Scraping per anno e keyword — codebase iniziale
- ✓ Paginazione automatica — codebase iniziale
- ✓ Download PDF opzionale — codebase iniziale
- ✓ Output CSV + JSON per anno + combinato multi-anno — codebase iniziale
- ✓ Riepiloghi aggregati (azioni, manovre, beneficiari, proponenti) — codebase iniziale
- ✓ **DATE-01**: Filtro per DATA_DA / DATA_A in scraper.py e delibere.py — Phase 1
- ✓ **DATE-02**: Auto-calcolo "settimana precedente" in GitHub Actions — Phase 2
- ✓ **AUTO-01**: Cron settimanale ogni lunedì + workflow_dispatch — Phase 2
- ✓ **AUTO-02**: Upload output su Google Drive via OAuth2 — Phase 3
- ✓ **AUTO-03**: Email di riepilogo SMTP con link Drive — Phase 3

### Active

- [ ] **PDF-01**: GitHub Actions scarica i PDF delle delibere ad ogni run automatico (SCARICA_LINK_PDF + SCARICA_PDF esposti come env var)
- [ ] **DRIVE-01**: Il sistema crea una sottocartella Drive per ogni run con nome che include il periodo (es. `FESR_2026_W23`)
- [ ] **DRIVE-02**: PDF + CSV riassuntivo vengono caricati nella sottocartella, non flat in GDRIVE_FOLDER_ID

### Out of Scope

- Interfaccia web — questo è uno strumento CLI/automazione
- Ricerca full-text nei PDF — solo download e catalogazione
- Database relazionale — output è flat file (CSV/JSON)

## Context

- Il portale SIIR restituisce HTML ISO-8859-1; il decoder è già in delibere.py
- `buildpayload()` e `buildpageparams()` hanno già i campi `dataAdozioneDa` / `dataAdozioneA` ma li lasciano vuoti
- Il formato data atteso dal portale è DD/MM/YYYY (confermato dai curl di esempio)
- L'esecuzione è sincrona, single-thread con rate limiting esplicito (PAUSA_SECONDI)
- GitHub Actions richiede credenziali Drive e SMTP nei GitHub Secrets

## Constraints

- **Tech stack**: Python 3 + requests + BeautifulSoup — nessun nuovo framework di scraping
- **Autenticazione portale**: Nessuna — il portale SIIR è pubblico, solo User-Agent header
- **Rate limiting**: Mantenere PAUSA_SECONDI tra le richieste per non sovraccaricare il portale
- **GitHub Actions**: Runner ubuntu-latest, Python 3.x standard

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Configurazione in cima a scraper.py invece di CLI args | Semplicità per utenti VS Code non tecnici | ⚠️ Revisit — rende difficile la parametrizzazione da Actions |
| Google Drive via Service Account | Nessun OAuth interattivo in CI/CD | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd:complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-06-11 — Milestone v1.1 started*
