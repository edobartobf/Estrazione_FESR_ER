---
phase: 05-drive-subfolder-upload
reviewed: 2026-06-11T00:00:00Z
depth: standard
files_reviewed: 2
files_reviewed_list:
  - upload_drive.py
  - test_upload_drive_subfolder.py
findings:
  critical: 1
  warning: 5
  info: 2
  total: 8
status: issues_found
---

# Phase 5: Code Review Report

**Reviewed:** 2026-06-11
**Depth:** standard
**Files Reviewed:** 2
**Status:** issues_found

## Summary

`upload_drive.py` refactors flat Drive upload into a dated-subfolder workflow. The core logic is
correct: `datesuffix()` is a faithful copy of `scraper.py:117-130`, the subfolder naming/fallback
is sound, and the `GITHUB_ENV` date injection from the "Calcola periodo" step correctly makes
`FESR_DATA_DA`/`FESR_DATA_A` available to the Drive step without explicit re-declaration.

Seven unit tests cover `datesuffix` and `nome_cartella` exhaustively and are logically correct
(the `upload_drive.date` mock target is right given the `from datetime import date` import).

Key concerns: one critical security issue (refresh token potentially exposed in error output), one
functional bug (missing output folder guard creates ghost subfolder on upload failure), and several
missing checks that will produce confusing failures in production.

---

## Critical Issues

### CR-01: RefreshError stack trace may leak OAuth2 refresh token

**File:** `upload_drive.py:46`
**Issue:** `creds.refresh(Request())` is called with no exception handling. When the refresh token
is invalid or expired, `google.auth.exceptions.RefreshError` is raised. Depending on the
`google-auth` library version, the exception message or `__repr__` of the `Credentials` object
may include the `refresh_token` value. In GitHub Actions, uncaught exceptions print a full
traceback to the public (or team-visible) log. An expired/revoked token leaking in logs is a
credential exposure risk.

**Fix:**
```python
try:
    creds.refresh(Request())
except Exception as e:
    print("ERROR: impossibile rinnovare le credenziali Google OAuth2.", file=sys.stderr)
    sys.exit(1)
return creds
```

---

## Warnings

### WR-01: Output folder existence is not validated before creating the Drive subfolder

**File:** `upload_drive.py:99` (and `upload_to_subfolder` line 63)
**Issue:** `main()` calls `create_subfolder()` unconditionally, then passes `output_folder` to
`upload_to_subfolder()`. If the `data/` output directory does not exist (e.g., the scraper step
was skipped or produced no output), `Path(folder_path).rglob("*")` raises `OSError`. The Drive
subfolder has already been created at that point, leaving an empty ghost subfolder in the user's
Drive on every failed run. Each re-run compounds this.

**Fix:** Validate the output folder before creating the subfolder:
```python
output_path = Path(output_folder)
if not output_path.is_dir():
    print(f"ERROR: cartella output '{output_folder}' non trovata.", file=sys.stderr)
    sys.exit(1)
subfolder_id = create_subfolder(service, folder_id, cartella_nome)
uploaded = upload_to_subfolder(output_folder, subfolder_id, service)
```

### WR-02: Malformed date env vars crash with an unhelpful ValueError

**File:** `upload_drive.py:18`
**Issue:** `datetime.strptime(d, "%d/%m/%Y")` will raise `ValueError` if `FESR_DATA_DA` or
`FESR_DATA_A` is set but does not match `DD/MM/YYYY` (e.g., a GitHub Actions `workflow_dispatch`
user types `2026-06-04` instead of `04/06/2026`). The traceback gives no indication which
environment variable is wrong.

**Fix:**
```python
def _tok(d):
    try:
        dt = datetime.strptime(d, "%d/%m/%Y")
    except ValueError:
        raise ValueError(f"Data non valida '{d}': formato atteso DD/MM/YYYY")
    return f"{dt.day:02d}{MESI[dt.month - 1]}"
```

### WR-03: `create_subfolder` does not guard against missing `"id"` in API response

**File:** `upload_drive.py:58`
**Issue:** `result["id"]` will raise `KeyError` if the Drive API response unexpectedly omits the
`id` field (e.g., a quota or permission error that nonetheless returns HTTP 200 with a partial
body). There is no check that `result` is non-empty or contains `"id"`.

**Fix:**
```python
folder_id = result.get("id")
if not folder_id:
    raise RuntimeError(f"Drive API non ha restituito un id per la cartella '{name}': {result}")
return folder_id
```

### WR-04: `upload_to_subfolder` silently continues after a per-file upload failure

**File:** `upload_drive.py:66-71`
**Issue:** If `service.files().create().execute()` raises for a specific file (network blip,
quota, MIME error), the exception propagates out of the loop immediately. Files uploaded before
the failure are orphaned in the subfolder; files after it are never uploaded. The caller in
`main()` gets an unhandled exception after `drive_url.txt` has not been written, which is
acceptable, but the partial state in Drive is invisible to the user.

This is consistent with the project's stated "no retry" policy, but the failure mode (partial
subfolder, no URL file, downstream email step reads stale `drive_url.txt` from a prior run)
should be acknowledged. At minimum, print a message identifying the failing file before the
exception surfaces.

**Fix:**
```python
result = service.files().create(
    body=metadata, media_body=media, fields="id,name"
).execute()
```
Wrap the call:
```python
try:
    result = service.files().create(
        body=metadata, media_body=media, fields="id,name"
    ).execute()
except Exception as e:
    print(f"ERRORE caricando {f.name}: {e}", file=sys.stderr)
    raise
```

### WR-05: Naming convention violations (underscores in function names)

**File:** `upload_drive.py:37, 50, 61`
**Issue:** The project's documented naming convention (`.planning/codebase/CONVENTIONS.md`)
mandates lowercase function names with no underscores: `fetchpage`, `parserows`, etc. The new
functions `build_credentials`, `create_subfolder`, and `upload_to_subfolder` all use underscores.
`datesuffix` and `nome_cartella` correctly follow the convention. This inconsistency will confuse
future contributors.

**Fix:** Rename to `buildcredentials`, `createsubfolder`, `uploadtosubfolder` to match the
established codebase pattern.

---

## Info

### IN-01: `drive_url.txt` is written to an implicit CWD-relative path

**File:** `upload_drive.py:102`
**Issue:** `Path("drive_url.txt").write_text(...)` resolves against the current working directory
at runtime. In GitHub Actions this is the repo root, which is correct, but there is no
documentation of this assumption and no constant or env var controls the output path.

**Fix:** Define a module-level constant for clarity:
```python
DRIVE_URL_FILE = Path("drive_url.txt")
```
and reference it consistently, or expose it as an env var if multi-environment use is expected.

### IN-02: Test suite has zero coverage for `create_subfolder` and `upload_to_subfolder`

**File:** `test_upload_drive_subfolder.py`
**Issue:** All 7 tests exercise only `datesuffix` and `nome_cartella`. The two functions that
interact with the Drive API (`create_subfolder`, `upload_to_subfolder`) and the credential builder
(`build_credentials`) have no tests. The functions could be unit-tested with `unittest.mock` to
patch `service.files().create().execute()` without needing real credentials.

**Fix:** Add at minimum:
- `test_create_subfolder_returns_id`: mock `service.files().create().execute()` returning
  `{"id": "abc123"}`, assert returned value is `"abc123"`.
- `test_upload_to_subfolder_empty_folder`: pass a real empty temp dir, assert `[]` is returned.

---

_Reviewed: 2026-06-11_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
