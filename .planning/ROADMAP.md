# ROADMAP — Milestone v1.1
# Drive PDF + Cartella Settimanale

## Overview

**Milestone goal:** Caricare i PDF delle delibere su Google Drive insieme al CSV riassuntivo, organizzati in una sottocartella denominata con il periodo di riferimento.

**Phases:** 2
**Requirements:** 3 (PDF-01, DRIVE-01, DRIVE-02)
**Coverage:** 3/3 ✓

---

## Phases

- [ ] **Phase 4: PDF Download in Actions** — Il workflow GitHub Actions scarica i PDF delle delibere abilitando SCARICA_LINK_PDF e SCARICA_PDF tramite env var
- [ ] **Phase 5: Drive Subfolder Upload** — upload_drive.py crea una sottocartella datata in Drive e carica PDF + CSV riassuntivo al suo interno

---

## Phase Details

### Phase 4: PDF Download in Actions
**Goal**: Lo scraping settimanale scarica anche i PDF delle delibere, senza modifiche manuali a scraper.py
**Depends on**: Nothing (v1.0 Phase 3 already complete)
**Requirements**: PDF-01
**Success Criteria** (what must be TRUE):
  1. Aggiungendo `FESR_SCARICA_PDF=true` e `FESR_SCARICA_LINK_PDF=true` come env var al run, i PDF vengono scaricati nella cartella `data/pdf/`
  2. Il workflow GitHub Actions attiva il download PDF ad ogni run automatico (cron) senza intervento manuale
  3. Se non ci sono delibere con link PDF, il run termina senza errori (zero PDF scaricati è un esito valido)
**Plans**: 2 plans
Plans:
- [ ] 04-01-PLAN.md — scraper.py: aggiunge `FESR_SCARICA_LINK_PDF` e `FESR_SCARICA_PDF` a `applysecrets()` con parsing bool (true/1/yes)
- [ ] 04-02-PLAN.md — fesr_scraper.yml: aggiunge `FESR_SCARICA_LINK_PDF: "true"` e `FESR_SCARICA_PDF: "true"` nell'env del passo "Esegui scraper"

### Phase 5: Drive Subfolder Upload
**Goal**: Ogni run carica i propri file (PDF + CSV riassuntivo) in una sottocartella Drive denominata con il periodo, lasciando GDRIVE_FOLDER_ID come cartella root organizzata per settimana
**Depends on**: Phase 4
**Requirements**: DRIVE-01, DRIVE-02
**Success Criteria** (what must be TRUE):
  1. Dopo un run, in `GDRIVE_FOLDER_ID` esiste una nuova sottocartella con nome tipo `FESR_04giu_10giu` (o `FESR_2026_W23`) contenente tutti i file caricati
  2. `drive_url.txt` contiene il link diretto alla sottocartella, non alla cartella root
  3. I run successivi creano nuove sottocartelle separate, non sovrascrivono quella precedente
  4. L'email di riepilogo linka alla sottocartella corretta (già usa drive_url.txt — invariato)
**Plans**: 1 plan
Plans:
- [ ] 05-01-PLAN.md — upload_drive.py: aggiunge `create_subfolder()`, rinomina logica upload in `upload_to_subfolder()`, nome cartella da `FESR_DATA_DA`/`FESR_DATA_A` (env, stessa convenzione datesuffix di scraper.py)

---

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 4. PDF Download in Actions | 0/2 | Pending | — |
| 5. Drive Subfolder Upload | 0/1 | Pending | — |
