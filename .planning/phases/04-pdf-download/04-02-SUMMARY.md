---
phase: 04-pdf-download
plan: "02"
subsystem: infra
tags: [github-actions, workflow, yaml, pdf-download, env-var]

# Dependency graph
requires:
  - phase: 04-01
    provides: "FESR_SCARICA_LINK_PDF e FESR_SCARICA_PDF esposti come env var in applysecrets()"
provides:
  - "FESR_SCARICA_LINK_PDF: \"true\" e FESR_SCARICA_PDF: \"true\" iniettati nel passo Esegui scraper di fesr_scraper.yml"
  - "Download PDF abilitato in ogni run automatico settimanale senza interventi manuali"
affects:
  - 04-pdf-download
  - github-actions-workflow

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Env var booleane hardcoded nel blocco env: del passo workflow per attivare funzionalità opzionali in CI/CD"

key-files:
  created: []
  modified:
    - .github/workflows/fesr_scraper.yml

key-decisions:
  - "FESR_SCARICA_PDF: \"true\" e FESR_SCARICA_LINK_PDF: \"true\" hardcoded nel workflow — entrambe necessarie per coerenza anche se l'implicazione prerequisito in applysecrets() garantirebbe LINK_PDF da sola"
  - "Valori stringa \"true\" con virgolette — coerente con il bool parsing val.strip().lower() in ('true','1','yes') già implementato in 04-01"

patterns-established:
  - "Attivazione funzionalità opzionale in CI/CD tramite env var stringa \"true\" nel blocco env: del passo workflow"

requirements-completed:
  - PDF-01

# Metrics
duration: 2min
completed: 2026-06-11
---

# Phase 04 Plan 02: PDF Download Workflow Activation Summary

**FESR_SCARICA_LINK_PDF e FESR_SCARICA_PDF aggiunti al passo "Esegui scraper" in fesr_scraper.yml, abilitando il download automatico dei PDF in ogni run settimanale GitHub Actions**

## Performance

- **Duration:** 2 min
- **Started:** 2026-06-11T12:40:00Z
- **Completed:** 2026-06-11T12:42:00Z
- **Tasks:** 1
- **Files modified:** 1 (.github/workflows/fesr_scraper.yml)

## Accomplishments

- `FESR_SCARICA_LINK_PDF: "true"` aggiunto al blocco `env:` del passo `Esegui scraper`
- `FESR_SCARICA_PDF: "true"` aggiunto al blocco `env:` del passo `Esegui scraper`
- Verifica YAML automatizzata passata: yaml.safe_load valido, entrambe le env var presenti e valorizzate `true`
- Tutti gli altri passi e variabili del workflow rimasti intatti

## Task Commits

Ogni task committato atomicamente:

1. **Task 1: Aggiungere FESR_SCARICA_LINK_PDF e FESR_SCARICA_PDF al passo Esegui scraper** - `19914e8` (feat)

**Piano metadata:** (da aggiungere con commit docs)

## Files Created/Modified

- `.github/workflows/fesr_scraper.yml` — passo `Esegui scraper` esteso con due env var per abilitare il download PDF

## Decisions Made

- Entrambe le variabili dichiarate esplicitamente anche se `applysecrets()` inferisce `SCARICA_LINK_PDF=True` da `SCARICA_PDF=True`: esplicitezza rende il workflow auto-documentante
- Indentazione a 10 spazi preservata (allineata a `FESR_KEYWORD`) — requisito YAML strutturale

## Deviations from Plan

None - piano eseguito esattamente come scritto.

## Issues Encountered

None.

## Threat Surface Scan

Nessuna nuova superficie di sicurezza introdotta. Le variabili aggiunte sono hardcoded nel repository (non da input esterni) e gestiscono solo il comportamento interno dello scraper, coerente con T-04-03 e T-04-04 nel threat model del piano.

## Next Phase Readiness

- PDF-01 completamente soddisfatto: applysecrets() legge le env var (04-01) e il workflow le passa (04-02)
- Il download PDF avverrà automaticamente in ogni run cron settimanale
- Prossimo obiettivo v1.1: DRIVE-01 (sottocartella Drive per ogni run) e DRIVE-02 (upload PDF + CSV nella sottocartella)

---
*Phase: 04-pdf-download*
*Completed: 2026-06-11*
