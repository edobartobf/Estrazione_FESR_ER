# Requirements — Milestone v1.0
# Filtro per periodo + Automazione settimanale

## Milestone Scope

Aggiungere il filtraggio per data al motore di scraping ed automatizzare il download settimanale via GitHub Actions con upload su Google Drive e notifica email.

---

## Active Requirements

### DATE — Filtro per periodo

- [ ] **DATE-01**: Utente può impostare `DATA_DA` e `DATA_A` in `scraper.py` per filtrare le delibere per data di adozione (formato DD/MM/YYYY)
- [ ] **DATE-02**: Se `DATA_DA` / `DATA_A` sono `None`, il comportamento rimane identico all'attuale (nessun filtro data, ricerca per anno intero)
- [ ] **DATE-03**: I file di output includono il periodo nella nomenclatura quando il filtro data è attivo (es. `delibere_2026_04giu_11giu_fesr.csv`)

### AUTO — Automazione GitHub Actions

- [ ] **AUTO-01**: GitHub Actions esegue lo scraping ogni lunedì mattina calcolando automaticamente il range lun–dom della settimana precedente
- [ ] **AUTO-02**: Il workflow è eseguibile manualmente (`workflow_dispatch`) con parametri opzionali per keyword e date custom
- [ ] **AUTO-03**: Al termine del run, tutti gli output (CSV/JSON + PDF) vengono caricati su una cartella Google Drive via Service Account JSON
- [ ] **AUTO-04**: Email di riepilogo inviata via SMTP ai destinatari configurati, con conteggio delibere, azioni trovate e link alla cartella Drive
- [ ] **AUTO-05**: Tutta la configurazione sensibile (Drive Service Account JSON, SMTP host/user/pass, email recipients) è gestita tramite GitHub Secrets — zero modifiche al codice tra un run e l'altro

---

## Future Requirements

- Invio differenziale (solo delibere nuove rispetto all'ultima run)
- Notifica Slack / Teams in aggiunta o alternativa all'email
- Filtro per tipo atto oltre che per keyword e periodo

---

## Out of Scope

- **Interfaccia web** — strumento CLI/automazione, non serve UI
- **Database relazionale** — output flat file (CSV/JSON) è sufficiente
- **Ricerca full-text nei PDF** — solo download e catalogazione
- **Date range cross-anno** — la ricerca per anno è mantenuta come granularità principale dell'API SIIR
- **Google Workspace** — si usa account personale con Service Account GCP gratuito

---

## Traceability

| REQ-ID | Phase | Status |
|--------|-------|--------|
| DATE-01 | Phase 1 | Pending |
| DATE-02 | Phase 1 | Pending |
| DATE-03 | Phase 1 | Pending |
| AUTO-01 | Phase 2 | Pending |
| AUTO-02 | Phase 2 | Pending |
| AUTO-05 | Phase 2 | Pending |
| AUTO-03 | Phase 3 | Pending |
| AUTO-04 | Phase 3 | Pending |
