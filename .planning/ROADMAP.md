# ROADMAP — Milestone v1.0
# Filtro per periodo + Automazione settimanale

## Overview

**Milestone goal:** Aggiungere il filtraggio per data al motore di scraping e automatizzare il download settimanale via GitHub Actions con notifica email e upload su Google Drive.

**Phases:** 3
**Requirements:** 8 (DATE-01–03, AUTO-01–05)
**Coverage:** 8/8 ✓

---

## Phases

- [x] **Phase 1: Date Filtering** - Il motore di scraping espone il filtro per periodo; i file di output riflettono il range usato
- [x] **Phase 2: GitHub Actions Skeleton** - Il workflow CI/CD esegue lo scraping settimanale e manuale con configurazione tramite Secrets
- [x] **Phase 3: Drive Upload + Email Notification** - Gli output vengono caricati su Google Drive e viene inviata email di riepilogo

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
**Plans**: 2 plans
Plans:
- [x] 01-01-PLAN.md — delibere.py: add datada/dataa to scraperesults, buildpayload, buildpageparams, fetchpage; DD/MM/YYYY validation; writesummaries date_suffix
- [x] 01-02-PLAN.md — scraper.py: DATA_DA/DATA_A config vars, datesuffix() helper, wire date tokens into filenames and forward to scraperesults/writesummaries

### Phase 2: GitHub Actions Skeleton
**Goal**: Lo scraping settimanale parte automaticamente ogni lunedì e può essere lanciato manualmente con parametri custom, senza credenziali nel codice
**Depends on**: Phase 1
**Requirements**: AUTO-01, AUTO-02, AUTO-05
**Success Criteria** (what must be TRUE):
  1. Il workflow si attiva ogni lunedì mattina (cron), calcola automaticamente il range lun–dom della settimana precedente e completa lo scraping FESR senza intervento manuale
  2. Avviando il workflow manualmente (workflow_dispatch) con keyword e date custom, il run utilizza quei parametri invece dei valori di default
  3. Rimuovendo i GitHub Secrets dal repository, il workflow fallisce con errore esplicito — zero credenziali hard-coded nel sorgente
**Plans**: 2 plans
Plans:
- [x] 02-01-PLAN.md — scraper.py: applysecrets() reads FESR_* env vars, called from main()
- [x] 02-02-PLAN.md — .github/workflows/fesr_scraper.yml: cron + dispatch, date computation, env-var driven scraper

### Phase 3: Drive Upload + Email Notification
**Goal**: Al termine di ogni run automatizzato, gli output sono disponibili su Google Drive e i destinatari ricevono un riepilogo via email
**Depends on**: Phase 2
**Requirements**: AUTO-03, AUTO-04
**Success Criteria** (what must be TRUE):
  1. Dopo un run completato, tutti i file di output (CSV/JSON + PDF) appaiono nella cartella Google Drive configurata, accessibili tramite il link nella email
  2. I destinatari configurati ricevono un'email con conteggio delle delibere trovate, azioni identificate e link diretto alla cartella Drive
  3. Un run con zero delibere trovate invia comunque email di riepilogo (conteggio = 0) invece di fallire silenziosamente
**Plans**: 3 plans
Plans:
- [x] 03-01-PLAN.md — upload_drive.py: Service Account upload to Drive, writes drive_url.txt
- [x] 03-02-PLAN.md — notify_email.py: SMTP email with delibere count, azioni, Drive link
- [x] 03-03-PLAN.md — .github/workflows/fesr_scraper.yml: activate Phase 3 steps

---

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Date Filtering | 2/2 | Complete | 2026-06-11 |
| 2. GitHub Actions Skeleton | 2/2 | Complete | 2026-06-11 |
| 3. Drive Upload + Email Notification | 3/3 | Complete | 2026-06-11 |
