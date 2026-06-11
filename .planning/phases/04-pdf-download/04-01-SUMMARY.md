---
phase: 04-pdf-download
plan: "01"
subsystem: infra
tags: [python, env-var, scraper, github-actions, pdf-download]

# Dependency graph
requires: []
provides:
  - "FESR_SCARICA_LINK_PDF e FESR_SCARICA_PDF esposti come env var in applysecrets()"
  - "Bool parsing coerente: true/1/yes → True; altro → False"
  - "Implicazione prerequisito: SCARICA_PDF=True forza SCARICA_LINK_PDF=True"
affects:
  - 04-pdf-download
  - github-actions-workflow

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Bool parsing via val.strip().lower() in ('true', '1', 'yes') — standard per tutte le env var booleane del progetto"
    - "Implicazione prerequisito inline in applysecrets(): se SCARICA_PDF then SCARICA_LINK_PDF=True"

key-files:
  created:
    - test_applysecrets_pdf_flags.py
  modified:
    - scraper.py

key-decisions:
  - "Bool parsing usa ('true', '1', 'yes') per coerenza con CONTEXT.md e altri env var override del progetto"
  - "Default hardcoded SCARICA_LINK_PDF=False / SCARICA_PDF=False rimangono invariati a livello modulo"
  - "Implicazione prerequisito fisica nel codice: SCARICA_PDF senza SCARICA_LINK_PDF non ha senso operativo"

patterns-established:
  - "Env var booleane FESR_*: val.strip().lower() in ('true', '1', 'yes')"

requirements-completed:
  - PDF-01

# Metrics
duration: 3min
completed: 2026-06-11
---

# Phase 04 Plan 01: PDF Download Env Vars Summary

**applysecrets() ora legge FESR_SCARICA_LINK_PDF e FESR_SCARICA_PDF con bool parsing true/1/yes e implicazione prerequisito automatica**

## Performance

- **Duration:** 3 min
- **Started:** 2026-06-11T12:33:34Z
- **Completed:** 2026-06-11T12:35:57Z
- **Tasks:** 1 (TDD: RED + GREEN)
- **Files modified:** 2 (scraper.py, test_applysecrets_pdf_flags.py)

## Accomplishments

- SCARICA_LINK_PDF e SCARICA_PDF aggiunti al global statement di applysecrets()
- Parsing FESR_SCARICA_LINK_PDF e FESR_SCARICA_PDF via os.environ.get() con bool coercion
- Implicazione prerequisito: se SCARICA_PDF diventa True, SCARICA_LINK_PDF viene forzato a True
- 6 test TDD tutti verdi; default hardcoded invariati

## Task Commits

Ogni task committato atomicamente (TDD: test → feat):

1. **RED: Test FESR_SCARICA_LINK_PDF / FESR_SCARICA_PDF** - `ce9805c` (test)
2. **GREEN: Implementazione in applysecrets()** - `0e6e4cb` (feat)

**Piano metadata:** (commit docs — da aggiungere)

_TDD: RED commit (test fallenti) → GREEN commit (implementazione)_

## Files Created/Modified

- `scraper.py` — applysecrets() esteso con parsing FESR_SCARICA_LINK_PDF e FESR_SCARICA_PDF
- `test_applysecrets_pdf_flags.py` — 6 test comportamentali TDD (tutti PASS)

## Decisions Made

- Bool parsing usa `val.strip().lower() in ("true", "1", "yes")` — coerente con linee guida CONTEXT.md e pattern già presenti nel progetto
- Default hardcoded `SCARICA_LINK_PDF = False` / `SCARICA_PDF = False` a livello modulo restano invariati: applysecrets() sovrascrive solo se env var presente
- Implicazione prerequisito fisica: SCARICA_PDF senza SCARICA_LINK_PDF non avrebbe senso operativo (non si possono scaricare PDF senza aver raccolto i link)

## Deviations from Plan

None - piano eseguito esattamente come scritto.

## Issues Encountered

None.

## TDD Gate Compliance

- RED gate: `ce9805c` — test(04-01): 6 test fallenti committati prima dell'implementazione
- GREEN gate: `0e6e4cb` — feat(04-01): implementazione committata, tutti i test passano

## User Setup Required

Per abilitare il download PDF in GitHub Actions, aggiungere al workflow YAML:

```yaml
env:
  FESR_SCARICA_LINK_PDF: "true"
  FESR_SCARICA_PDF: "true"
```

Oppure solo `FESR_SCARICA_PDF: "true"` (l'implicazione prerequisito forzerà automaticamente FESR_SCARICA_LINK_PDF).

## Next Phase Readiness

- PDF-01 soddisfatto: SCARICA_LINK_PDF e SCARICA_PDF ora configurabili da GitHub Actions via env var
- Pronto per Phase 04-02: aggiornamento del workflow GitHub Actions per passare le env var e gestire l'upload dei PDF su Drive

---
*Phase: 04-pdf-download*
*Completed: 2026-06-11*
