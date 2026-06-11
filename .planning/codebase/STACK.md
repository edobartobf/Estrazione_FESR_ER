# Technology Stack

**Analysis Date:** 2026-06-11

## Languages

**Primary:**
- Python 3 - All source code (`scraper.py`, `delibere.py`, `analisi.py`)

**Secondary:**
- None detected

## Runtime

**Environment:**
- Python 3 (no version pin in `requirements.txt` or `.python-version` file detected)

**Package Manager:**
- pip — dependency declarations in `requirements.txt`
- Lockfile: Not present (no `requirements.lock` or `pip.lock`)

## Frameworks

**Core:**
- None (plain Python scripts, no web framework)

**Testing:**
- Not detected (no test files, no pytest/unittest config)

**Build/Dev:**
- No build system detected
- VS Code is the documented IDE (`.vscode/` in `.gitignore`)

## Key Dependencies

**Critical:**
- `requests>=2.31.0` (`requirements.txt`) — all HTTP communication: search form POST, paginated GET requests, PDF streaming downloads
- `beautifulsoup4>=4.12.0` (`requirements.txt`) — HTML parsing of the SIIR portal's ISO-8859-1 encoded pages

**Standard Library (no install required):**
- `csv` — writing CSV output files (`delibere.py`, `analisi.py`)
- `json` — writing JSON output files (`delibere.py`)
- `re` — regex-based data extraction from delibera text fields (`delibere.py`)
- `time` — rate-limiting delays between HTTP requests (`delibere.py`)
- `pathlib.Path` — all filesystem path handling (`scraper.py`, `delibere.py`, `analisi.py`)
- `collections.Counter` — frequency counting for summary reports (`delibere.py`)
- `urllib.parse` — URL joining and decoding (`delibere.py`)
- `argparse` — CLI argument parsing for `analisi.py`

## Configuration

**Environment:**
- No environment variables — all configuration is hardcoded constants at the top of `scraper.py`
- Key runtime parameters: `ANNI`, `KEYWORD`, `CARTELLA_OUTPUT`, `SCARICA_LINK_PDF`, `SCARICA_PDF`, `MAX_PAGINE`, `MAX_PDF`, `PAUSA_SECONDI`, `TIMEOUT_SECONDI`

**Build:**
- No build config files

## Platform Requirements

**Development:**
- Python 3 with `pip`
- Recommended: install dependencies into a virtual environment (`.venv/`, `venv/`, `env/` are all `.gitignore`d)
- Documented entry point: run `scraper.py` directly via "Run Python File" in VS Code

**Production:**
- No deployment target — this is a local data extraction pipeline
- Output is written to `data/` (gitignored): CSV files, JSON files, summary CSVs, and optionally a `data/pdf/` subdirectory

---

*Stack analysis: 2026-06-11*
