# ROADMAP — Milestone v1.0
# Filtro per periodo + Automazione settimanale

## Overview

**Milestone goal:** Aggiungere il filtraggio per data al motore di scraping e automatizzare il download settimanale via GitHub Actions con notifica email e upload su Google Drive.

**Phases:** 3
**Requirements:** 8 (DATE-01–03, AUTO-01–05)
**Coverage:** 8/8 ✓

---

## Phases

- [ ] **Phase 1: Date Filtering** - Il motore di scraping espone il filtro per periodo; i file di output riflettono il range usato
- [ ] **Phase 2: GitHub Actions Skeleton** - Il workflow CI/CD esegue lo scraping settimanale e manuale con configurazione tramite Secrets
- [ ] **Phase 3: Drive Upload + Email Notification** - Gli output vengono caricati su Google Drive e viene inviata email di riepilogo

---

## Phase Details

### Phase 1: Date Filtering
**Goal**: Gli analisti possono filtrare le delibere per periodo di adozione senza toccare il codice del portale
**Depends on**: Nothing (first phase)
**Requirements**: DATE-01, DATE-02, DATE-03
**Success Criteria** (what must be TRUE):
  1. Impostando DATA_DA e DATA_A in scraper.py, il CSV/JSON risultante contiene solo delibere adottate nel periodo specificato
  2. Con DATA_DA / DATA_A lasciati a None, il comportamento è identico all'attuale (nessun filtro, anno intero)
  3. I file di output generati con filtro attivo includono le date nel nome (es. `delibere_2026_04giu_11giu_fesr.csv`)
**Plans**: TBD

### Phase 2: GitHub Actions Skeleton
**Goal**: Lo scraping settimanale parte automaticamente ogni lunedì e può essere lanciato manualmente con parametri custom, senza credenziali nel codice
**Depends on**: Phase 1
**Requirements**: AUTO-01, AUTO-02, AUTO-05
**Success Criteria** (what must be TRUE):
  1. Il workflow si attiva ogni lunedì mattina (cron), calcola automaticamente il range lun–dom della settimana precedente e completa lo scraping FESR senza intervento manuale
  2. Avviando il workflow manualmente (workflow_dispatch) con keyword e date custom, il run utilizza quei parametri invece dei valori di default
  3. Rimuovendo i GitHub Secrets dal repository, il workflow fallisce con errore esplicito — zero credenziali hard-coded nel sorgente
**Plans**: TBD

### Phase 3: Drive Upload + Email Notification
**Goal**: Al termine di ogni run automatizzato, gli output sono disponibili su Google Drive e i destinatari ricevono un riepilogo via email
**Depends on**: Phase 2
**Requirements**: AUTO-03, AUTO-04
**Success Criteria** (what must be TRUE):
  1. Dopo un run completato, tutti i file di output (CSV/JSON + PDF) appaiono nella cartella Google Drive configurata, accessibili tramite il link nella email
  2. I destinatari configurati ricevono un'email con conteggio delle delibere trovate, azioni identificate e link diretto alla cartella Drive
  3. Un run con zero delibere trovate invia comunque email di riepilogo (conteggio = 0) invece di fallire silenziosamente
**Plans**: TBD

---

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Date Filtering | 0/0 | Not started | - |
| 2. GitHub Actions Skeleton | 0/0 | Not started | - |
| 3. Drive Upload + Email Notification | 0/0 | Not started | - |
