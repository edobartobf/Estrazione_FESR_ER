# Coding Conventions

**Analysis Date:** 2026-06-11

## Naming Patterns

**Files:**
- All lowercase, no separators: `delibere.py`, `scraper.py`, `analisi.py`
- Names match the domain concern (delibere = library, scraper = entry point, analisi = CLI tool)

**Functions:**
- All lowercase, no underscores, camelCase-free: `fetchpage`, `parserows`, `enrichrecord`, `buildpayload`, `cleantext`, `writecsv`, `writejson`, `writesummaries`, `countfield`, `splitvalues`
- Verb-noun structure is the standard: `fetchfirstpage`, `findpdflink`, `downloadpdf`, `buildpageparams`, `buildparser`, `readcsv`

**Variables:**
- Short, lowercase, no underscores within a function scope: `allrecords`, `totalpages`, `pdfcount`, `csvpath`, `jsonpath`
- Loop variables follow English single words: `anno`, `record`, `page`, `chunk`, `row`, `value`
- Multi-word variables collapse words together: `maxpages`, `maxpdf`, `outputfolder`, `includelinks`

**Constants (module-level):**
- Full UPPERCASE with underscores: `BASE_URL`, `BASE_DIR`, `HEADERS`, `FIELDNAMES`
- Config variables in `scraper.py` also UPPERCASE: `ANNI`, `KEYWORD`, `CARTELLA_OUTPUT`, `SCARICA_PDF`, `MAX_PAGINE`, `PAUSA_SECONDI`, `TIMEOUT_SECONDI`

**CSV field names:**
- snake_case strings used as dictionary keys and CSV column headers: `anno_ricerca`, `keyword_ricerca`, `numero_adozione`, `tipo_manovra`, `pdf_url`, `dettaglio_url`

**Parameters:**
- Lowercase, no underscores, abbreviated where idiomatic: `anno`, `keyword`, `maxpages`, `delay`, `timeout`, `outputfolder`, `fallback`

## Code Style

**Formatting:**
- No formatter config file present (no `.prettierrc`, no `pyproject.toml`, no `setup.cfg`)
- Style is consistent with PEP 8 in spacing and blank lines, but deviates on naming (no underscores in function/variable names)
- 4-space indentation throughout
- Max line length appears to be ~100 characters; long strings broken with implicit string concatenation inside parentheses (see `HEADERS` in `delibere.py` line 16-17)

**Linting:**
- No linter configuration present (no `.flake8`, no `pylintrc`, no `ruff.toml`)

**Imports:**
- Standard library first, then third-party, separated by a blank line
- Imports sorted alphabetically within each group
- Example from `delibere.py`:
  ```python
  import csv
  import json
  import re
  import time
  from collections import Counter
  from pathlib import Path
  from urllib.parse import unquote, urljoin

  import requests
  from bs4 import BeautifulSoup
  ```

**Module structure:**
- Module-level constants at top after imports
- Functions in dependency order (helpers before callers)
- `main()` function as entry point
- `if __name__ == "__main__": main()` guard at bottom

## Error Handling

**Pattern:** Minimal — rely on `raise_for_status()` for HTTP errors; no custom exception types; no try/except blocks anywhere in the codebase.

**HTTP errors:** `response.raise_for_status()` is called in `fetchfirstpage`, `fetchpage`, `findpdflink`, and `downloadpdf`. This lets `requests.HTTPError` propagate uncaught to the caller.

**Missing data:** Handled defensively with fallback values rather than exceptions:
- `parsecounter` returns a default dict with `total_pages: 1` when the counter table is absent
- `parseoggetto` checks `if link` before accessing link attributes
- `findpdflink` returns `""` when `dettaglio` is falsy or no link is found
- `enrichrecord` uses `.get("oggetto", "")` to guard against missing keys

**No retry logic:** HTTP requests are not retried on failure.

## Logging

**Framework:** None. All output uses `print()` directly.

**Patterns:**
- Progress lines use f-strings with Italian-language messages:
  ```python
  print(f"Trovati {totalrecords} risultati in {totalpages} pagine.")
  print(f"Pagina {page}/{totalpages}: {len(records)} righe, totale {len(allrecords)}.")
  print(f"Anno {anno} completato.")
  ```
- Blank `print("")` lines used as visual separators between run sections
- No log levels, no timestamps, no structured logging

## Comment Style

**Section headers:** Used only in `scraper.py` config block with `# ===...===` banner style:
```python
# ============================================================
# MODIFICA SOLO QUESTA SEZIONE
# ============================================================
```

**Inline comments:** Not present in `delibere.py` or `analisi.py`; code is self-documenting via function and variable names.

**Block comments:** Configuration section in `scraper.py` uses multi-line `#` comments to document usage examples and typical configurations.

**No docstrings:** No function or module docstrings anywhere in the codebase.

## Language-Specific Idioms

**`pathlib.Path` for all file I/O:** Used exclusively — no `os.path`. File writing uses `path.open(...)` and `path.write_text(...)`.

**`requests.Session`:** A single session is created per `scraperesults()` call and reused across all HTTP requests for connection pooling.

**Generator expressions and comprehensions:**
- Dict comprehensions: `{key for record in records for key in record.keys()}`
- List comprehensions: `[str(year) for year in range(...)]`, `[part for part in parts if part]`
- `next((...), "")` used for safe first-match extraction from a generator

**`Counter` from `collections`:** Used in `countfield()` for frequency aggregation.

**`re` flags passed inline:** `flags=re.I` used consistently rather than compiled patterns; `re.compile(...)` used only inside `soup.find()` calls where a compiled pattern is expected.

**String normalization:** Whitespace collapsed via `re.sub(r"\s+", " ", value or "").strip()` in `cleantext()`, called throughout.

**`or` for fallback values:** `value or ""` and `record.get("field", "")` are the standard defensive patterns.

**Italian variable and message names in `scraper.py`:** Config-level variables (`ANNI`, `CARTELLA_OUTPUT`, `SCARICA_PDF`, `PAUSA_SECONDI`) and print messages use Italian; library-level names in `delibere.py` use English.

---

*Convention analysis: 2026-06-11*
