# Requirements — Milestone v1.1
# Drive PDF + Cartella Settimanale

## Milestone Scope

Abilitare il download dei PDF delle delibere nell'automazione settimanale e organizzare gli upload su Drive in una sottocartella denominata con il periodo di riferimento, contenente PDF + CSV riassuntivo.

---

## Active Requirements

### PDF — Download PDF nell'automazione

- [x] **PDF-01**: Il workflow GitHub Actions scarica i PDF delle delibere ad ogni run automatico (`SCARICA_LINK_PDF=True` e `SCARICA_PDF=True` esposti tramite env var `FESR_SCARICA_LINK_PDF` / `FESR_SCARICA_PDF` in `applysecrets()`)

### DRIVE — Organizzazione sottocartella Drive

- [ ] **DRIVE-01**: Per ogni run, `upload_drive.py` crea una sottocartella in `GDRIVE_FOLDER_ID` con nome che include il periodo di riferimento (es. `FESR_2026_W23` o `FESR_04giu_10giu`)
- [ ] **DRIVE-02**: PDF scaricati + CSV riassuntivo vengono caricati nella sottocartella, non flat in `GDRIVE_FOLDER_ID`; `drive_url.txt` contiene il link diretto alla sottocartella

---

## Validated (da v1.0)

- ✓ **DATE-01**: Filtro per DATA_DA / DATA_A — Phase 1
- ✓ **DATE-02**: Auto-calcolo "settimana precedente" in GitHub Actions — Phase 2
- ✓ **DATE-03**: Nome file include il periodo quando filtro attivo — Phase 1
- ✓ **AUTO-01**: Cron settimanale ogni lunedì + workflow_dispatch — Phase 2
- ✓ **AUTO-02**: workflow_dispatch con parametri opzionali — Phase 2
- ✓ **AUTO-03**: Upload su Google Drive — Phase 3
- ✓ **AUTO-04**: Email di riepilogo SMTP — Phase 3
- ✓ **AUTO-05**: Configurazione sensibile via GitHub Secrets — Phase 2

---

## Future Requirements

- Invio differenziale (solo delibere nuove rispetto all'ultimo run)
- Notifica Slack / Teams in aggiunta o alternativa all'email
- Filtro per tipo atto oltre che per keyword e periodo
- MAX_PDF configurabile via env var per limitare i download in Actions

---

## Out of Scope

- **Interfaccia web** — strumento CLI/automazione, non serve UI
- **Database relazionale** — output flat file (CSV/JSON) è sufficiente
- **Ricerca full-text nei PDF** — solo download e catalogazione
- **Date range cross-anno** — granularità per anno mantenuta come principale
- **Deduplicazione tra run** — ogni run è indipendente

---

## Traceability

| REQ-ID | Phase | Status |
|--------|-------|--------|
| PDF-01 | Phase 4 | Complete (04-01 + 04-02, 2026-06-11) |
| DRIVE-01 | Phase 5 | Pending |
| DRIVE-02 | Phase 5 | Pending |
