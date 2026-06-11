# Codebase Concerns

**Analysis Date:** 2026-06-11

---

## Tech Debt

**Configuration baked into source code (`scraper.py`):**
- Issue: All run parameters (`ANNI`, `KEYWORD`, `SCARICA_PDF`, `MAX_PAGINE`, `MAX_PDF`, `PAUSA_SECONDI`, `TIMEOUT_SECONDI`, `CARTELLA_OUTPUT`) are module-level constants in `scraper.py` lines 47–57. The user is instructed to edit the file directly before each run.
- Files: `scraper.py` lines 4–57
- Impact: Produces noisy git diffs on every use; risks accidental commit of debug settings (e.g. `MAX_PAGINE = 2` is the current committed value — a test limit — not a production setting); makes the tool unusable in non-interactive pipelines.
- Fix approach: Move parameters to CLI arguments (argparse) or a config file (e.g. `config.toml` / `.env`), mirroring the pattern already used in `analisi.py`.

**`MAX_PAGINE = 2` committed in default state (`scraper.py` line 54):**
- Issue: The committed default artificially caps scraping at two pages. Any user who runs the script without reading the comments will get a silent, incomplete dataset.
- Files: `scraper.py` line 54
- Impact: Silent data truncation; no warning is printed when `maxpages` is hit.
- Fix approach: Default to `None` (unlimited), or print an explicit warning when pagination is capped.

**No dedicated entry-point / `__main__` guard in `delibere.py`:**
- Issue: `delibere.py` is a library but also imported directly. It contains no runnable `main()`, yet has module-level mutable globals (`BASE_URL`, `BASE_DIR`, `HEADERS`, `FIELDNAMES`) that would be re-executed on every import.
- Files: `delibere.py` lines 13–43
- Impact: Low risk today, but makes future testing or mocking of constants harder.

---

## Security Concerns

**No input sanitisation on `keyword` before embedding in HTTP requests (`delibere.py`):**
- Issue: The `keyword` value from `scraper.py` is passed verbatim into `buildpayload()` (line 60) and `buildpageparams()` (line 72) as a form/query parameter. No stripping, length check, or allow-list validation is applied.
- Files: `delibere.py` lines 50–85, `scraper.py` line 48
- Impact: A malicious or malformed keyword could cause unexpected server-side behaviour or corrupt output filenames (via the suffix construction at `scraper.py` line 86).
- Fix approach: Validate keyword against an allow-list of expected characters; enforce max length.

**User-Agent spoofing (`delibere.py` lines 15–18):**
- Issue: The `HEADERS` dict presents a Chrome/Linux browser identity. This violates most website terms of service and could constitute a legal/ethical risk, particularly since the target is a regional government portal.
- Files: `delibere.py` lines 15–18
- Impact: Account/IP bans; potential legal exposure under Italian law on automated access to public-administration portals.
- Fix approach: Use a transparent bot User-Agent that identifies the tool and its purpose (e.g. `EstrazioneFESR/1.0 (+https://github.com/...)`).

**No verification of downloaded PDF content type (`delibere.py` lines 245–255):**
- Issue: `downloadpdf()` streams whatever the server returns without checking `Content-Type`. A redirect to an HTML error page would be silently saved as a `.pdf` file on disk.
- Files: `delibere.py` lines 245–255
- Impact: Corrupt output files that appear successful; downstream PDF readers will fail without a clear error source.
- Fix approach: Assert `response.headers.get("Content-Type", "").startswith("application/pdf")` before writing.

**Filename derived from server-controlled `Content-Disposition` header (`delibere.py` lines 237–242):**
- Issue: `contentfilename()` trusts the server-supplied filename directly after a `Path(...).name` strip. A crafted header (e.g. `filename="../../evil.pdf"`) could still produce unexpected paths depending on OS behaviour.
- Files: `delibere.py` lines 237–242
- Impact: Potential path traversal if the server or a MITM response is malicious.
- Fix approach: Sanitise the filename: strip all path separators, restrict to alphanumeric + `.`, `-`, `_`; enforce a max length.

---

## Missing Error Handling

**`response.raise_for_status()` used without a try/except anywhere in the call chain (`delibere.py`):**
- Issue: `fetchfirstpage()` (line 89), `fetchpage()` (line 97), `findpdflink()` (line 229), and `downloadpdf()` (line 248) all call `raise_for_status()` but no caller wraps them in try/except. A single HTTP 5xx or network timeout aborts the entire run and loses all progress.
- Files: `delibere.py` lines 88–99, 225–255; `scraper.py` lines 88–98
- Impact: A transient server error on page 47 of 50 discards all collected data.
- Fix approach: Wrap individual page/PDF fetches in try/except with retry logic (e.g. `tenacity`) and continue-on-error semantics; checkpoint collected records to disk periodically.

**No retry logic for PDF downloads (`delibere.py` line 286–295 in `scraperesults`):**
- Issue: PDF download failures (timeouts, 404s, 503s) silently skip the file without recording the failure. The `pdf_file` key is only set on success; there is no `pdf_error` field.
- Files: `delibere.py` lines 282–295
- Impact: Silently incomplete datasets; no way to identify which PDFs failed without re-running everything.
- Fix approach: Set `record["pdf_error"]` on failure; log a warning; optionally retry.

**`analisi.py` crashes on empty CSV (`analisi.py` line 26):**
- Issue: `records[0]` is accessed unconditionally to infer `anno` and `keyword`. If the CSV is empty or the file does not exist, an `IndexError` or `FileNotFoundError` is raised with no user-friendly message.
- Files: `analisi.py` lines 24–26
- Impact: Confusing traceback for non-developer users.
- Fix approach: Check `if not records` and exit with a clear message; wrap `Path.open()` in a try/except for missing files.

**`parsecounter()` silently returns defaults on parse failure (`delibere.py` lines 102–115):**
- Issue: If the regex does not match, the function returns `total_pages: 1` and `total_records: 0`. This means a failed parse causes the scraper to silently stop after page 1 and report zero records found, giving no indication that pagination detection failed.
- Files: `delibere.py` lines 102–115
- Impact: Silent data loss; the run appears to complete normally.
- Fix approach: Log a warning when the counter table or regex is not found so the operator can investigate.

---

## Scalability Limitations

**Sequential PDF fetching with a fixed sleep delay (`delibere.py` lines 283–296):**
- Issue: Each PDF link lookup and each download is sequential, with a `time.sleep(delay)` call between each. For large datasets (hundreds of delibere per year, multiple years) this becomes a bottleneck on order of hours.
- Files: `delibere.py` lines 258–305; `scraper.py` lines 57, 95
- Impact: A multi-year full run with PDF download could take many hours on a single thread.
- Fix approach: Use `concurrent.futures.ThreadPoolExecutor` for I/O-bound PDF downloads; keep the delay per-worker to remain polite to the server.

**All records accumulated in memory before writing (`delibere.py` lines 271–305; `scraper.py` lines 81–106):**
- Issue: The complete record list for a year (potentially thousands of entries) is held in a Python list before being written to CSV/JSON. For very large date ranges this grows proportionally.
- Files: `scraper.py` lines 81, 106; `delibere.py` line 271
- Impact: Negligible for typical FESR volumes (hundreds of records), but a structural limit for repurposing the tool on larger datasets.
- Fix approach: Stream-write records to CSV as each page is scraped; accumulate only IDs or minimal data for the combined multi-year file.

**Hard-coded page size of 10 (`delibere.py` lines 63, 78):**
- Issue: `PAG_SIZE_ricerca_delibere` and `PAG_SIZE_RICERCA_DELIBERE` are hard-coded to `"10"`. The README notes the server ignores larger values, but this is not re-validated or configurable.
- Files: `delibere.py` lines 63, 78
- Impact: Number of HTTP requests cannot be reduced if the server ever supports larger pages.

---

## Fragile Code Patterns

**HTML scraping tied to undocumented internal portal structure (`delibere.py`):**
- Issue: The entire scraper depends on specific HTML element IDs (`ricerca_delibere_tr_`, `contatore`), CSS classes (`linkatto`), column index positions (cells[0]–cells[6]), and POST/GET parameter names. All of these can change without notice when the regional portal is updated.
- Files: `delibere.py` lines 102–131, 196–222, 225–234
- Impact: Any portal update silently breaks the scraper; there are no structural assertions to detect format changes.
- Fix approach: Add sanity-check assertions (e.g. warn if zero rows are parsed on a page that the counter says is non-empty); add a `--dry-run` mode that validates HTML structure without saving data.

**Cell access by positional index with only a minimum-length guard (`delibere.py` lines 201–220):**
- Issue: `cells[0]` through `cells[6]` are accessed after only checking `len(cells) < 7`. If the portal adds or reorders columns the field mapping silently misassigns data without raising an error.
- Files: `delibere.py` lines 201–220
- Impact: Silently wrong data in CSV/JSON output.
- Fix approach: Parse cells by header text or known label, or at minimum assert the expected column headers during the first-page parse.

**`leggianni()` does not validate year values (`scraper.py` lines 61–75):**
- Issue: Integer conversion of range boundaries (`int(start.strip())`) raises `ValueError` on any non-numeric input without a descriptive error message. There is no check that years are plausible (e.g. 1900–2100).
- Files: `scraper.py` lines 61–75
- Impact: Confusing traceback for user typos in the `ANNI` variable.
- Fix approach: Wrap in try/except with a clear message; validate range bounds.

**`enrichrecord()` regex patterns are brittle for Italian legal text (`delibere.py` lines 181–193):**
- Issue: Patterns for CUP codes, DGR references, monetary amounts, and beneficiary extraction use fixed Italian-language strings (e.g. `"A FAVORE"`, `"BENEFICIARI"`) and assume specific formatting. Italian administrative text varies considerably in practice.
- Files: `delibere.py` lines 169–193
- Impact: False negatives (fields left empty) and occasional false positives (wrong data extracted) without any confidence signal in the output.
- Fix approach: Add a `_confidence` or `_raw_match` debug field; write unit tests against a corpus of real `oggetto` strings.

---

## Missing Features Implied by the Code

**No resume / incremental mode:**
- The tool re-scrapes all pages from scratch on every run. There is no checkpoint file, no deduplication against an existing CSV, and no way to resume an interrupted download. The `data/` folder is completely regenerated each run.
- Files: `scraper.py` lines 78–119; `delibere.py` lines 258–305
- Fix approach: Before scraping, load existing record IDs from the output CSV; skip already-seen `protocollo` values; resume PDF downloads from the `pdf/` folder.

**No logging framework — only `print()` statements:**
- All progress reporting uses bare `print()` calls (`delibere.py` lines 281–298; `scraper.py` lines 84–127). There is no log level, no timestamps, no file log, and no way to suppress output in library use.
- Files: `delibere.py` lines 281, 298; `scraper.py` lines 84, 108–126
- Fix approach: Replace with Python's `logging` module; default to `INFO`; allow `--quiet` / `--verbose` CLI flags.

**`analisi.py` does not support multi-year combined CSV files:**
- `writesummaries()` derives the output suffix from `anno` and `keyword`. When called from `analisi.py` the `--anno` flag must be provided manually for multi-year files, and the suffix logic does not match the `anni[0]_anni[-1]` pattern used by `scraper.py` line 114.
- Files: `analisi.py` lines 26–29; `scraper.py` lines 114–119
- Fix approach: Align the suffix logic or support a `--suffix` override argument in `analisi.py`.

**No deduplication across years:**
- When scraping a year range, the combined CSV (`delibere_..._tutti_gli_anni.csv`) is a naive concatenation of per-year lists. If a delibera's `data_adozione` straddles the search window it may appear in multiple year queries.
- Files: `scraper.py` lines 113–119
- Fix approach: Deduplicate by `protocollo` before writing the combined file.

---

## Dependencies at Risk

**Only two runtime dependencies (`requirements.txt`):**
- `beautifulsoup4>=4.12.0` and `requests>=2.31.0` are both well-maintained. However, minimum versions only (`>=`) are pinned, meaning `pip install` on a fresh environment may pull a future breaking release.
- Files: `requirements.txt`
- Fix approach: Pin exact versions in a lock file (`pip-compile` / `pip freeze > requirements-lock.txt`) for reproducible installs.

**No HTML parser explicitly specified for BeautifulSoup (`delibere.py` lines 197, 230):**
- Issue: `BeautifulSoup(html, "html.parser")` uses the built-in stdlib parser. This parser is tolerant but slower and less consistent than `lxml`. If a developer installs `lxml` it will not be used automatically, and switching parsers can produce different parse trees for malformed HTML.
- Files: `delibere.py` lines 197, 230
- Impact: Subtle, environment-dependent parse differences.
- Fix approach: Document the chosen parser; consider adding `lxml` as an optional dependency and noting the trade-off.

**No `python_requires` or `.python-version` file:**
- The project does not declare its minimum Python version anywhere. f-strings and `pathlib` require Python 3.6+; `Path.open()` with `newline=` is 3.x-only. A user on Python 2 would get a confusing syntax error.
- Files: `requirements.txt`, absent `pyproject.toml` / `setup.cfg`
- Fix approach: Add a `.python-version` file (e.g. `3.11`) and/or a `pyproject.toml` with `requires-python = ">=3.9"`.

---

## Performance Concerns

**`decodehtml()` decodes the full response body to a string before parsing (`delibere.py` line 47):**
- Issue: `response.content.decode("ISO-8859-1")` loads the complete response into memory as a Python string, then passes it to BeautifulSoup which re-encodes it internally. For large pages or responses this doubles memory usage.
- Files: `delibere.py` line 47
- Impact: Negligible for typical delibere page sizes (~50 KB), but worth noting for robustness.
- Fix approach: Pass `response.content` directly to BeautifulSoup with `from_encoding="ISO-8859-1"`.

**`countfield()` iterates all records once per summary field (`delibere.py` lines 328–336; `writesummaries` lines 343–348):**
- Issue: `writesummaries()` calls `countfield()` four times, each doing a full pass over `records`. For large datasets this is four O(n) passes where one would suffice.
- Files: `delibere.py` lines 328–348
- Impact: Negligible at current data volumes; worth addressing before scaling to tens of thousands of records.
- Fix approach: Compute all counters in a single pass.

---

*Concerns audit: 2026-06-11*
