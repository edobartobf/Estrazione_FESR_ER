# Phase 1: Date Filtering - Context

**Gathered:** 2026-06-11
**Status:** Ready for planning

<domain>
## Phase Boundary

Expose date-range filtering in the scraping engine so analysts can limit results to a specific period of adoption (DATA_DA / DATA_A in DD/MM/YYYY format). The portal's existing API fields (`dataAdozioneDa`, `dataAdozioneA`) are already wired in the payload builders — they just need to be plumbed through. Output filenames reflect the active date range when filtering is on. Backwards compatibility (None = no filter) is a hard requirement.

</domain>

<decisions>
## Implementation Decisions

### Date API Design
- Add `datada=None` and `dataa=None` parameters to `scraperesults()` in `delibere.py`
- Portal-side filtering: pass dates directly to `buildpayload()` and `buildpageparams()` — avoids downloading unneeded pages
- Validate in `scraperesults()` before the loop starts — fail fast with `ValueError` on bad format
- Both `None` = no filter — identical behavior to current (DATE-02 compliance)
- Multi-year runs: same date range applied to each year's scraperesults call

### Output Naming
- Date tokens use Italian abbreviated month names: `04giu`, `11giu` (matches REQUIREMENTS example `delibere_2026_04giu_11giu_fesr.csv`)
- Suffix format when filter active: `delibere_{anno}_{da}_{a}_{keyword}.csv`
- If only one date is set, include just that token in suffix
- Summary CSVs also get the date suffix when filter is active

### scraper.py Integration
- Add `DATA_DA = None` and `DATA_A = None` to the config section with a comment showing example values
- Pass `DATA_DA`/`DATA_A` to `scraperesults()` call
- Compute date-aware filename suffix in `scraper.py:main()` — scraper.py owns naming, delibere.py owns filtering
- No CLI args added — scraper.py stays config-file style (consistent with existing approach)

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `buildpayload(anno, keyword)` — already has `dataAdozioneDa: ""` and `dataAdozioneA: ""`
- `buildpageparams(anno, keyword, page)` — already has `DATAADOZIONEDA: ""` and `DATAADOZIONEEA: ""`
- `scraperesults()` — orchestration function to extend with datada/dataa params
- `leggianni()` in scraper.py — year parser, already handles int/str/range/list

### Established Patterns
- Module-level functions, no classes anywhere
- All config as module-level vars at top of scraper.py (lines 47–57)
- `scraper.py` is a thin wrapper; all logic in `delibere.py`
- Filename suffix pattern: `f"{anno}_{KEYWORD.lower()}".replace(" ", "_")`

### Integration Points
- `delibere.py:buildpayload()` line 50 — add datada/dataa params and wire to payload keys
- `delibere.py:buildpageparams()` line 67 — same for DATAADOZIONEDA/DATAADOZIONEEA
- `delibere.py:scraperesults()` line 258 — add datada/dataa, pass down to fetch functions
- `scraper.py` config block lines 47–57 — add DATA_DA, DATA_A vars
- `scraper.py:main()` lines 78–130 — compute suffix, pass dates to scraperesults()

</code_context>

<specifics>
## Specific Ideas

- Date format in filename: `04giu` = zero-padded day + 3-letter Italian month abbreviation (gen/feb/mar/apr/mag/giu/lug/ago/set/ott/nov/dic)
- Example filename per requirements: `delibere_2026_04giu_11giu_fesr.csv`
- The portal uses DD/MM/YYYY — validate with simple regex or datetime.strptime

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>
