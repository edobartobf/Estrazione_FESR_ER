# Phase 4: PDF Download in Actions - Context

**Gathered:** 2026-06-11
**Status:** Ready for planning
**Mode:** Auto-generated (infrastructure phase — discuss skipped)

<domain>
## Phase Boundary

Esporre `SCARICA_LINK_PDF` e `SCARICA_PDF` come env var (`FESR_SCARICA_LINK_PDF` / `FESR_SCARICA_PDF`) in `applysecrets()` dentro `scraper.py`, e abilitarle nel workflow GitHub Actions. L'obiettivo è che il cron settimanale scarichi automaticamente i PDF delle delibere senza richiedere modifiche manuali al codice.

</domain>

<decisions>
## Implementation Decisions

### Claude's Discretion
Tutte le scelte implementative sono a discrezione di Claude — fase di pura configurazione/infrastruttura.

Linee guida:
- Bool parsing per env var: `val.strip().lower() in ("true", "1", "yes")` — pattern coerente con le altre variabili Python
- Se `FESR_SCARICA_PDF=true` ma `FESR_SCARICA_LINK_PDF` non è impostato, abilitare anche `SCARICA_LINK_PDF` automaticamente (i link sono prerequisito del download)
- Aggiungere entrambe le env var al passo "Esegui scraper" nel workflow con valore `"true"`

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `applysecrets()` in `scraper.py` — pattern esistente per override tramite env var `FESR_*`
- Variabili globali `SCARICA_LINK_PDF` e `SCARICA_PDF` già presenti in `scraper.py` (hardcoded `False`)

### Established Patterns
- Pattern env var parsing in `applysecrets()`: `val = os.environ.get("FESR_XYZ"); if val: GLOBAL = val`
- Per bool serve parsing esplicito: `.lower() in ("true", "1", "yes")`
- Il passo "Esegui scraper" nel workflow già riceve `FESR_KEYWORD`, `FESR_DATA_DA`, `FESR_DATA_A`

### Integration Points
- `scraper.py:applysecrets()` — dove aggiungere le 2 nuove variabili
- `.github/workflows/fesr_scraper.yml` passo `Esegui scraper` — dove aggiungere le env var

</code_context>

<specifics>
## Specific Ideas

- `FESR_SCARICA_PDF=true` implica automaticamente `FESR_SCARICA_LINK_PDF=true` (link è prerequisito fisico del download)
- Se l'env var non è impostata o è vuota, comportamento invariato (False come default)

</specifics>

<deferred>
## Deferred Ideas

- `FESR_MAX_PDF` env var per limitare il numero di PDF scaricati (utile per test rapidi) — future requirement
- `FESR_PAUSA_SECONDI` env var per configurare il rate limiting da Actions

</deferred>
