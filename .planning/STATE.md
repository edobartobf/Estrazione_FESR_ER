---
milestone: "v1.0"
name: "Filtro per periodo + Automazione settimanale"
status: planning
progress:
  phases_total: 3
  phases_done: 0
  tasks_total: 0
  tasks_done: 0
---

## Current Position

Phase: Not started (roadmap defined, awaiting phase planning)
Plan: —
Status: Roadmap created
Last activity: 2026-06-11 — Roadmap v1.0 created (3 phases)

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
- Plan Phase 1: Date Filtering (DATE-01, DATE-02, DATE-03)
