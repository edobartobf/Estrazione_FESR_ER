# Codebase Structure

**Analysis Date:** 2026-06-11

## Directory Layout

```
Estrazione_FESR_ER/
├── scraper.py          # Interactive entry point; holds all config variables
├── delibere.py         # Core library: scraping, parsing, enrichment, I/O
├── analisi.py          # CLI tool to regenerate summaries from an existing CSV
├── requirements.txt    # Python dependencies (beautifulsoup4, requests)
├── README.md           # Usage documentation
├── .gitignore          # Ignores __pycache__, venvs, .venv, .idea, .vscode, data/
└── data/               # Runtime output (git-ignored, created on first run)
    ├── delibere_<anno>_<keyword>.csv
    ├── delibere_<anno>_<keyword>.json
    ├── riepilogo_azioni_<anno>_<keyword>.csv
    ├── riepilogo_manovre_<anno>_<keyword>.csv
    ├── riepilogo_beneficiari_<anno>_<keyword>.csv
    ├── riepilogo_proponenti_<anno>_<keyword>.csv
    └── pdf/
        └── <downloaded PDF files>
```

## Directory Purposes

**Project root:**
- Purpose: Contains all source files. No subdirectories for source code; the project is flat.
- Key files: `scraper.py`, `delibere.py`, `analisi.py`.

**`data/` (runtime, git-ignored):**
- Purpose: All output produced by a scraping run lands here.
- Contains: per-year and multi-year CSV/JSON files, four summary CSV files per run, and a `pdf/` subdirectory for downloaded PDFs.
- Generated: Yes — created automatically by `writecsv()` / `writejson()` / `downloadpdf()` using `Path.mkdir(parents=True, exist_ok=True)`.
- Committed: No — excluded by `.gitignore`.

## Key File Locations

**Entry Points:**
- `scraper.py`: Interactive scraping run; edit config variables at the top, then execute.
- `analisi.py`: CLI for re-running summary aggregation on a previously generated CSV.

**Core Library:**
- `delibere.py`: All HTTP, parsing, enrichment, PDF, and file-write logic. Imported by both entry points.

**Configuration:**
- `requirements.txt`: Two runtime dependencies — `beautifulsoup4>=4.12.0`, `requests>=2.31.0`.
- `.gitignore`: Excludes `data/`, virtual-environment directories, IDE folders, and `__pycache__`.

**Documentation:**
- `README.md`: Quick-start guide and output file reference.

## Naming Conventions

**Files:**
- Source: lowercase, no separators (`scraper.py`, `delibere.py`, `analisi.py`).
- Output CSVs/JSONs: `delibere_<anno>_<keyword>.{csv,json}`, `riepilogo_<campo>_<anno>_<keyword>.csv`; spaces in keyword replaced with `_`.

**Functions:**
- All lowercase, no underscores (`scraperesults`, `parserows`, `enrichrecord`, `writecsv`).

**Constants:**
- All uppercase with underscores (`BASE_URL`, `FIELDNAMES`, `SCARICA_PDF`).

**Variables in `scraper.py`:**
- All uppercase (they act as configuration constants for the run).

## Module Relationships

```
scraper.py
  └── imports from delibere.py:
        scraperesults, writecsv, writejson, writesummaries

analisi.py
  └── imports from delibere.py:
        writesummaries

delibere.py
  └── imports: csv, json, re, time, collections.Counter,
               pathlib.Path, urllib.parse.{unquote,urljoin},
               requests, bs4.BeautifulSoup
```

`delibere.py` has no internal imports from the project — it is the only shared module.

## Where to Add New Code

**New scraping field or enrichment rule:**
- Edit `enrichrecord()` in `delibere.py` (line 181).
- Add the field name to `FIELDNAMES` in `delibere.py` (lines 20–43) to include it in CSV output.

**New output format (e.g., Excel, SQLite):**
- Add a new `write*()` function in `delibere.py`.
- Call it from `scraper.py:main()` alongside the existing `writecsv()` / `writejson()` calls.

**New summary/aggregate report:**
- Add a `count*()` function in `delibere.py` following the `countfield()` pattern.
- Call it inside `writesummaries()` in `delibere.py` (line 343).

**New CLI tool:**
- Create a new top-level `.py` file that imports from `delibere.py`.
- Follow the `analisi.py` pattern: `argparse` for arguments, `if __name__ == "__main__": main()` guard.

**New config parameter for scraping:**
- Add the variable at the top of `scraper.py` (lines 47–57) and pass it to `scraperesults()` in `scraper.py:main()`.
- Add the matching parameter to `scraperesults()` in `delibere.py` (line 258).

## Special Directories

**`data/`:**
- Purpose: Runtime output — CSVs, JSONs, summary CSVs, PDFs.
- Generated: Yes, on first run.
- Committed: No (`.gitignore` entry: `data/`).

**`.planning/`:**
- Purpose: GSD planning documents (architecture maps, phase plans).
- Generated: By GSD tooling.
- Committed: Yes (not in `.gitignore`).

---

*Structure analysis: 2026-06-11*
