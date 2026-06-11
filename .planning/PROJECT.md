# Estrazione FESR ER

## What This Is

Scraper Python che scarica le deliberazioni della giunta regionale dell'Emilia-Romagna dal portale SIIR, filtra per keyword (default "FESR") e produce file CSV/JSON strutturati con download opzionale dei PDF allegati.
Usato da analisti per monitorare le delibere FESR 2021-2027 senza accesso manuale al portale.

## Core Value

Estrarre tutte le delibere FESR di un periodo in modo affidabile e senza intervento manuale, con output pronti all'analisi.

## Current Milestone: v1.0 — Filtro per periodo + Automazione settimanale

**Goal:** Aggiungere il filtraggio per data al motore di scraping e automatizzare il download settimanale via GitHub Actions con notifica email e upload su Google Drive.

**Target features:**
- Filtro per data (DATA_DA / DATA_A) in scraper.py e delibere.py
- Auto-calcolo "settimana precedente" per i parametri data
- GitHub Actions: cron settimanale, download FESR + PDF
- Upload output (PDF + CSV/JSON) su Google Drive
- Email di riepilogo ai destinatari configurati

## Requirements

### Validated

- ✓ Scraping per anno e keyword — codebase iniziale
- ✓ Paginazione automatica — codebase iniziale
- ✓ Download PDF opzionale — codebase iniziale
- ✓ Output CSV + JSON per anno + combinato multi-anno — codebase iniziale
- ✓ Riepiloghi aggregati (azioni, manovre, beneficiari, proponenti) — codebase iniziale

### Active

- [ ] **DATE-01**: Utente può specificare DATA_DA e DATA_A per filtrare le delibere per periodo
- [ ] **DATE-02**: Scraper auto-calcola "settimana precedente" quando viene richiesta l'automazione
- [ ] **AUTO-01**: GitHub Actions esegue il download ogni settimana (cron lunedì mattina)
- [ ] **AUTO-02**: Output (PDF + CSV/JSON) viene caricato su Google Drive dopo ogni run
- [ ] **AUTO-03**: Email di riepilogo inviata ai destinatari configurati al termine del run

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
*Last updated: 2026-06-11 — Milestone v1.0 started*
