# Testing Patterns

**Analysis Date:** 2026-06-11

## Test Framework

**Runner:** None — no testing framework is installed or configured.

**Config:** No `pytest.ini`, `setup.cfg`, `pyproject.toml`, `tox.ini`, or `unittest` discovery configuration present.

**Run Commands:**
```bash
# No test commands available — no tests exist
```

## Test File Organization

**Location:** No test files exist in the repository.

**Naming:** No test naming convention established.

**Structure:** No test directory (`tests/`, `test/`) present.

## Test Coverage

**Unit tests:** None.

**Integration tests:** None.

**End-to-end tests:** None.

## What Is Tested (Manually)

The `scraper.py` config block documents an informal manual test pattern:

```python
# Fast manual smoke test — first 2 pages only, no PDF download:
SCARICA_LINK_PDF = False
SCARICA_PDF = False
MAX_PAGINE = 2
MAX_PDF = None
```

This is a human-run verification approach, not an automated test.

## Testing Gaps

**All logic is untested.** Key functions with no coverage:

- `leggianni` (`scraper.py`) — parses year strings into lists; has branching logic for int, range string, list, and plain string inputs. Unit tests would be straightforward.
- `cleantext` (`delibere.py`) — regex whitespace normalization.
- `parsecounter` (`delibere.py`) — parses pagination info from HTML; regex-dependent, brittle against site changes.
- `parserows` (`delibere.py`) — full HTML row parsing; depends on site HTML structure.
- `enrichrecord` (`delibere.py`) — regex extraction of CUP codes, DGR references, importi, azioni, beneficiari. High complexity, high regex surface area, no tests.
- `classifymanovra` (`delibere.py`) — keyword classification with ordered priority rules; logic errors would be silent.
- `extractbeneficiario` (`delibere.py`) — regex extraction with multiple fallback patterns.
- `findall` (`delibere.py`) — deduplicating regex search with tuple-group handling.
- `splitvalues` (`delibere.py`) — semicolon-split utility.
- `countfield` (`delibere.py`) — frequency aggregation with `Counter`.
- All I/O functions (`writecsv`, `writejson`, `writesummaries`) — no filesystem or output format tests.

**HTTP layer is untested:** `fetchfirstpage`, `fetchpage`, `findpdflink`, `downloadpdf` make live network calls with no mocking layer or fixture HTML provided.

**`analisi.py` CLI is untested:** argument parsing (`buildparser`) and the `main()` flow have no tests.

## Dependencies at Risk from No Tests

- `enrichrecord` uses 8 regex patterns against free-text `oggetto` fields scraped from a live government portal. Site HTML changes or unexpected text formats will produce silent wrong output with no test safety net.
- `parsecounter` will silently return `total_pages: 1` if the counter table structure changes, causing the scraper to download only the first page without error.
- `classifymanovra` priority ordering (e.g., "liquidazione saldo" must be checked before "liquidazione") is enforced only by list position — no test guards this ordering.

## Recommended Test Approach

If tests are added, the natural fit for this codebase is `pytest` with `pytest-mock` or `responses` for HTTP mocking:

```bash
pip install pytest pytest-mock responses
pytest tests/
```

Priority areas for first tests:
1. `leggianni` — pure function, easy to cover all branches.
2. `classifymanovra` — pure function, priority ordering is a real regression risk.
3. `enrichrecord` — pure function; fixture `oggetto` strings can drive regex correctness.
4. `parsecounter` and `parserows` — use saved HTML fixtures (local `.html` files) to avoid live network dependency.

---

*Testing analysis: 2026-06-11*
