<!-- refreshed: 2026-06-11 -->
# Architecture

**Analysis Date:** 2026-06-11

## System Overview

```text
┌────────────────────────────────────────────────────────────────┐
│                    Entry Points                                 │
│                                                                 │
│   scraper.py (interactive run)    analisi.py (CLI re-analysis) │
└───────────────────┬────────────────────────┬───────────────────┘
                    │                        │
                    ▼                        │
┌───────────────────────────────────────┐    │
│          delibere.py — core library   │◄───┘
│                                       │
│  scraperesults()   ← orchestration    │
│  fetchpage()       ← HTTP             │
│  parserows()       ← HTML parsing     │
│  enrichrecord()    ← field extraction │
│  findpdflink()     ← detail page      │
│  downloadpdf()     ← PDF download     │
│  writecsv()        ← CSV output       │
│  writejson()       ← JSON output      │
│  writesummaries()  ← aggregate CSVs   │
└───────────────────┬───────────────────┘
                    │
                    ▼
┌────────────────────────────────────────┐
│  data/  (runtime output, git-ignored)  │
│  ├── delibere_<suffix>.csv             │
│  ├── delibere_<suffix>.json            │
│  ├── riepilogo_azioni_<suffix>.csv     │
│  ├── riepilogo_manovre_<suffix>.csv    │
│  ├── riepilogo_beneficiari_<suffix>.csv│
│  ├── riepilogo_proponenti_<suffix>.csv │
│  └── pdf/  (downloaded PDFs)           │
└────────────────────────────────────────┘
```

## Component Responsibilities

| Component | Responsibility | File |
|-----------|----------------|------|
| `scraper.py` | User-facing entry point; holds all config variables; calls library; writes per-year and multi-year outputs | `scraper.py` |
| `analisi.py` | CLI tool for regenerating summary CSVs from an existing CSV file without re-scraping | `analisi.py` |
| `delibere.py` | Core library: HTTP session, pagination, HTML parsing, field extraction, enrichment, PDF handling, file I/O | `delibere.py` |
| `data/` | Runtime output directory; all files are generated and git-ignored | `data/` |

## Pattern Overview

**Overall:** Single-library pipeline with two thin entry-point scripts.

**Key Characteristics:**
- All business logic lives in `delibere.py`; the two entry-point scripts are minimal wrappers.
- No classes; the entire codebase uses module-level functions.
- No external framework; HTTP is handled via `requests.Session` directly.
- Synchronous, single-threaded execution with explicit `time.sleep()` throttling between requests.

## Layers

**Configuration layer:**
- Purpose: Expose tunable parameters for a single run.
- Location: top of `scraper.py` (lines 47–57).
- Contains: `ANNI`, `KEYWORD`, `CARTELLA_OUTPUT`, `SCARICA_LINK_PDF`, `SCARICA_PDF`, `MAX_PAGINE`, `MAX_PDF`, `PAUSA_SECONDI`, `TIMEOUT_SECONDI`.
- Depends on: nothing.
- Used by: `main()` in `scraper.py`.

**HTTP + pagination layer (`delibere.py`):**
- Purpose: Build request payloads, fetch pages, and decode ISO-8859-1 HTML from the SIIR portal.
- Functions: `buildpayload()`, `buildpageparams()`, `fetchfirstpage()`, `fetchpage()`, `decodehtml()`.
- Details: Page 1 uses HTTP POST; subsequent pages use HTTP GET with query parameters. The portal always returns 10 records per page.

**Parsing + enrichment layer (`delibere.py`):**
- Purpose: Extract structured records from raw HTML and derive semantic fields from free-text `oggetto`.
- Functions: `parserows()`, `parseoggetto()`, `parsecounter()`, `cleantext()`, `enrichrecord()`.
- Enrichment functions called by `enrichrecord()`: `findall()`, `classifymanovra()`, `extractbeneficiario()`.
- Derived fields: `programma`, `azioni`, `priorita`, `cup`, `dgr`, `determinazioni`, `tipo_manovra`, `beneficiario`, `importi`.

**PDF handling layer (`delibere.py`):**
- Purpose: Optionally follow each record's detail URL to find the PDF link, then download it.
- Functions: `findpdflink()`, `downloadpdf()`, `contentfilename()`.
- Output: files written to `data/pdf/`.

**Output layer (`delibere.py`):**
- Purpose: Write scraped records and aggregate summaries to disk.
- Functions: `writecsv()`, `writejson()`, `writesummary()`, `writesummaries()`, `countfield()`, `splitvalues()`.
- Schema: canonical field order defined in `FIELDNAMES` constant (lines 20–43); extra fields appended automatically.

## Data Flow

### Primary Scraping Path

1. `scraper.py:main()` parses `ANNI` via `leggianni()` and iterates over years.
2. For each year: calls `delibere.scraperesults()` with all options.
3. `scraperesults()` opens a `requests.Session`, then loops over pages:
   - `fetchpage()` → raw ISO-8859-1 HTML string.
   - `parserows()` → list of record dicts + pagination counter.
   - For each record: optionally calls `findpdflink()` (detail page GET) and `downloadpdf()`.
4. `scraperesults()` returns the complete list of record dicts for that year.
5. `scraper.py:main()` calls `writecsv()`, `writejson()`, `writesummaries()` for each year.
6. If multiple years were requested, a combined CSV/JSON/summary is also written.

### Re-Analysis Path (analisi.py)

1. `analisi.py:main()` parses CLI arguments (`csvfile`, `--anno`, `--keyword`, `--output-dir`).
2. Reads an existing CSV with `readcsv()`.
3. Derives `anno` and `keyword` from CLI args or from the first record's metadata fields.
4. Calls `delibere.writesummaries()` to regenerate the four summary CSVs in place.

### State Management

- No in-memory shared state between runs; each `main()` invocation is fully self-contained.
- The `requests.Session` object lives only within a single `scraperesults()` call.

## Key Abstractions

**Record dict:**
- Purpose: Represents one delibera (regional act) with all scraped and derived fields.
- Created in: `delibere.parserows()` (line 206).
- Enriched in: `delibere.enrichrecord()` (line 181).
- Schema: `FIELDNAMES` list in `delibere.py` (lines 20–43) plus optional `pdf_file` key added at runtime.

**`FIELDNAMES` constant:**
- Purpose: Defines canonical CSV column order and acts as the agreed record schema.
- Location: `delibere.py` lines 20–43.

## Entry Points

**`scraper.py` (interactive):**
- Location: `scraper.py`
- Triggers: "Run Python File" in VS Code, or `python scraper.py` from shell.
- Responsibilities: Parse year range, loop over years, orchestrate scraping and output for each.

**`analisi.py` (CLI):**
- Location: `analisi.py`
- Triggers: `python analisi.py <csvfile> [--anno ...] [--keyword ...] [--output-dir ...]`
- Responsibilities: Load existing CSV, regenerate summary files without re-scraping.

## Architectural Constraints

- **Threading:** Single-threaded. No async, no workers. `time.sleep()` is used explicitly between HTTP requests to avoid hammering the portal.
- **Global state:** `BASE_URL`, `BASE_DIR`, `HEADERS`, `FIELDNAMES` are module-level constants in `delibere.py`. They are read-only and safe.
- **Circular imports:** None. Dependency is one-directional: `scraper.py` → `delibere.py` and `analisi.py` → `delibere.py`.
- **Encoding:** The SIIR portal returns ISO-8859-1; `decodehtml()` in `delibere.py` handles the conversion explicitly.
- **Page size:** The portal ignores requested page sizes and always returns 10 records; the scraper follows this hard limit.

## Anti-Patterns

### Configuration embedded in source file

**What happens:** All runtime parameters (`ANNI`, `SCARICA_PDF`, etc.) are plain variables at the top of `scraper.py`.
**Why it's wrong:** Changing parameters requires editing source code; no way to invoke different configurations without modifying the file.
**Do this instead:** Accept CLI arguments (like `analisi.py` does) or read from a config file, keeping `scraper.py` untouched between runs.

## Error Handling

**Strategy:** No explicit try/except blocks. `requests` calls use `.raise_for_status()`, which raises `HTTPError` on 4xx/5xx responses. Any network error or parse failure propagates as an unhandled exception and terminates the run.

**Patterns:**
- `response.raise_for_status()` used after every HTTP call in `fetchfirstpage()`, `fetchpage()`, `findpdflink()`, `downloadpdf()`.
- Regex non-matches return empty strings or default dicts; no exceptions raised for missing data.

## Cross-Cutting Concerns

**Logging:** `print()` statements only. Progress is printed to stdout (page counts, record counts, file paths).
**Validation:** None beyond implicit HTML structure assumptions in `parserows()`.
**Authentication:** None. The SIIR portal is publicly accessible; only a browser-like `User-Agent` header is set.

---

*Architecture analysis: 2026-06-11*
