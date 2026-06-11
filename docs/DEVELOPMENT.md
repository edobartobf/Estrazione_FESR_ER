<!-- generated-by: gsd-doc-writer -->
# Development Guide

Guide for developers who want to modify, extend, or contribute to the FESR scraper pipeline.

## Local Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd Estrazione_FESR_ER
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it:

- Windows: `.venv\Scripts\activate`
- macOS/Linux: `source .venv/bin/activate`

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

For local development there is no separate dev-dependencies file — the two runtime dependencies in `requirements.txt` cover all local runs.

### 4. Configure a run

Open `scraper.py` and edit the configuration block at the top of the file (lines marked `# MODIFICA SOLO QUESTA SEZIONE`). Key variables:

| Variable | Default | Description |
|---|---|---|
| `ANNI` | `"2026"` | Year(s) to scrape — integer, range string `"2023-2026"`, or list |
| `KEYWORD` | `""` | Optional search keyword |
| `SOLO_DELIBERE` | `True` | Filter to Delibere di Giunta only (`tipoAtto=DL`) |
| `SCARICA_LINK_PDF` | `False` | Resolve the PDF URL for each record |
| `SCARICA_PDF` | `False` | Download the PDF file to `data/pdf/` |
| `MAX_PAGINE` | `None` | Limit pages per year (None = all) |
| `MAX_PDF` | `None` | Limit total PDFs downloaded (None = all) |
| `DATA_DA` | `None` | Date range start `DD/MM/YYYY` |
| `DATA_A` | `None` | Date range end `DD/MM/YYYY` |

### 5. Run the scraper

Execute `scraper.py` directly:

```bash
python scraper.py
```

Output files are written to the `data/` directory (git-ignored, created automatically on first run).

---

## Build Commands

There is no build step — all modules are plain Python scripts. The commands available are:

| Command | Description |
|---|---|
| `python scraper.py` | Run a full scraping pass using the config variables at the top of `scraper.py` |
| `python analisi.py <csvfile>` | Regenerate summary CSVs from an existing scrape output |
| `pip install -r requirements.txt` | Install runtime dependencies |

### `analisi.py` arguments

```bash
python analisi.py data/delibere_2026_.csv \
    --anno 2026 \
    --keyword FESR \
    --output-dir data/
```

| Argument | Required | Description |
|---|---|---|
| `csvfile` | Yes | Path to a CSV file produced by `scraper.py` |
| `--anno` | No | Year label used in output file names (inferred from CSV if omitted) |
| `--keyword` | No | Keyword label used in output file names (inferred from CSV if omitted) |
| `--output-dir` | No | Output directory (defaults to same directory as the input CSV) |

---

## Code Style

There is no formatter or linter configuration file in the repository. The codebase follows these conventions, which contributors must respect:

### Naming

- **Functions and variables:** all lowercase, no underscores, words collapsed together — `fetchpage`, `parserows`, `allrecords`, `totalpages`.
- **Module-level constants:** `ALL_CAPS_WITH_UNDERSCORES` — `BASE_URL`, `FIELDNAMES`, `PAUSA_SECONDI`.
- **Config variables in `scraper.py`:** all uppercase, same as constants — `ANNI`, `KEYWORD`, `SCARICA_PDF`.
- **CSV field names (dict keys and column headers):** `snake_case` — `anno_ricerca`, `numero_adozione`, `pdf_url`.

### Formatting

- 4-space indentation throughout.
- Approximate 100-character line limit; long strings broken with implicit concatenation inside parentheses.
- Standard library imports first, then third-party, separated by one blank line. Imports alphabetically ordered within each group.
- Module structure: constants → helpers → callers → `main()` → `if __name__ == "__main__": main()`.

### Patterns to follow

- Use `pathlib.Path` for all file I/O — no `os.path`.
- Use `response.raise_for_status()` for HTTP errors — no manual status code checks.
- Use `value or ""` and `dict.get("key", "")` for defensive missing-data handling — no try/except for missing keys.
- Use `print()` for all progress output — no logging framework.
- No docstrings on functions (project convention); prefer self-documenting names.

---

## Branch Conventions

No formal branch naming convention is documented. The repository uses a `main` branch as the default. A suggested informal convention:

- `feat/<short-description>` — new feature or scraping capability
- `fix/<short-description>` — bug fix
- `docs/<short-description>` — documentation changes

---

## PR Process

This is an internal tool repository. To propose a change:

1. Fork or branch from `main`.
2. Make changes and test locally with a smoke run (`MAX_PAGINE = 2`, `SCARICA_PDF = False`).
3. Ensure no `data/` output files are committed (the directory is git-ignored).
4. Open a pull request against `main` describing what the change does and why.
5. No formal review process is documented — approval by the repository owner is sufficient.

---

## Extending the Codebase

The `.planning/codebase/STRUCTURE.md` file documents where to add new code for common extension scenarios:

- **New scraping field:** Edit `enrichrecord()` in `delibere.py` and add the field to `FIELDNAMES`.
- **New output format (Excel, SQLite):** Add a `write*()` function in `delibere.py` and call it from `scraper.py:main()`.
- **New summary report:** Add a `count*()` function in `delibere.py` and register it inside `writesummaries()`.
- **New CLI tool:** Create a new top-level `.py` file that imports from `delibere.py`, following the `analisi.py` pattern.
- **New config parameter:** Add the variable at the top of `scraper.py` and pass it through to `scraperesults()` in `delibere.py`.

---

## Related Documentation

- [GETTING-STARTED.md](GETTING-STARTED.md) — prerequisites and first-run instructions
- [CONFIGURATION.md](CONFIGURATION.md) — full environment variable reference for CI/GitHub Actions
- [ARCHITECTURE.md](ARCHITECTURE.md) — module structure and data flow
