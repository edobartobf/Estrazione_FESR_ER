---
milestone: "v1.0"
name: "Filtro per periodo + Automazione settimanale"
status: in_progress
progress:
  phases_total: 3
  phases_done: 0
  tasks_total: 0
  tasks_done: 0
---

## Current Position

Phase: 1 — Date Filtering (planned, ready to execute)
Plan: 2 plans in 2 waves
Status: Ready to execute
Last activity: 2026-06-11 — Phase 1 planned (2 plans: 01-01-PLAN.md, 01-02-PLAN.md)

## Project Reference

See: .planning/PROJECT.md (updated 2026-06-11)

**Core value:** Estrarre tutte le delibere FESR di un periodo in modo affidabile e senza intervento manuale, con output pronti all'analisi.
**Current focus:** Phase 1 — Date Filtering

## Accumulated Context

### Decisions
- buildpayload() e buildpageparams() già hanno campi data — serve solo esporli
- Drive via Service Account GCP (no OAuth interattivo in CI/CD)
- Configurazione sensibile gestita interamente via GitHub Secrets

### Blockers
(none)

### Todos
- Execute Phase 1: Date Filtering
