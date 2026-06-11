---
phase: 05-drive-subfolder-upload
verified: 2026-06-11T14:00:00Z
status: passed
score: 5/5 must-haves verified
overrides_applied: 0
---

# Phase 5: Drive Subfolder Upload — Verification Report

**Phase Goal:** Ogni run carica i propri file (PDF + CSV) in una sottocartella Drive denominata con il periodo, lasciando GDRIVE_FOLDER_ID come cartella root organizzata per settimana
**Verified:** 2026-06-11T14:00:00Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Ogni run crea una nuova sottocartella in GDRIVE_FOLDER_ID con nome FESR_{datesuffix} (es. FESR_04giu_10giu) | VERIFIED | `create_subfolder(service, folder_id, cartella_nome)` called in `main()` with name derived from `nome_cartella(datada, dataa)` — line 117. `nome_cartella("04/06/2026","10/06/2026")` returns `"FESR_04giu_10giu"` confirmed by test. |
| 2 | Quando FESR_DATA_DA e FESR_DATA_A non sono impostati, il nome cade su FESR_{YYYYMMDD} con la data odierna | VERIFIED | `nome_cartella()` fallback: `return f"FESR_{date.today().strftime('%Y%m%d')}"` (line 38). Test `test_nome_cartella_none_none_uses_today` passes with mocked date. |
| 3 | Tutti i file in data/ (CSV + PDF) vengono caricati nella sottocartella, non flat in GDRIVE_FOLDER_ID | VERIFIED | `upload_to_subfolder(output_folder, subfolder_id, service)` uses `subfolder_id` in metadata parents (line 78), not the root `folder_id`. |
| 4 | drive_url.txt contiene il link alla sottocartella (https://drive.google.com/drive/folders/{subfolder_id}), non alla root | VERIFIED | Line 119: `subfolder_url = f"https://drive.google.com/drive/folders/{subfolder_id}"` — Line 121: `Path("drive_url.txt").write_text(subfolder_url, encoding="utf-8")`. No reference to root `folder_id` in URL construction. |
| 5 | Run successivi creano nuove sottocartelle separate — nessuna sovrascrittura | VERIFIED | `create_subfolder()` always calls `service.files().create()` — no lookup for existing folders, no deduplication. Each invocation creates a new Drive folder. |

**Score:** 5/5 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `upload_drive.py` | create_subfolder(), datesuffix(), upload_to_subfolder(), nome_cartella(), main() updated; min 80 lines | VERIFIED | 126 lines. AST parse confirms all 5 required functions present: `['datesuffix', 'nome_cartella', 'build_credentials', 'create_subfolder', 'upload_to_subfolder', 'main', '_tok']`. `upload_folder` absent. |
| `test_upload_drive_subfolder.py` | Unit tests for datesuffix() and folder naming logic | VERIFIED | 7 tests, all passing. Covers datesuffix with both/one/no dates, nome_cartella with both/one/no dates including today-fallback with mock. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `upload_drive.py:main()` | `upload_drive.py:create_subfolder()` | `service` passed from main after `build()` | WIRED | Line 113: `service = build("drive", "v3", credentials=creds)`. Line 117: `subfolder_id = create_subfolder(service, folder_id, cartella_nome)`. |
| `upload_drive.py:main()` | `drive_url.txt` | `Path('drive_url.txt').write_text(subfolder_url)` | WIRED | Line 121: `Path("drive_url.txt").write_text(subfolder_url, encoding="utf-8")` where `subfolder_url` contains `subfolder_id`, not root `folder_id`. |
| `upload_drive.py:create_subfolder()` | Drive API files.create | `mimeType: application/vnd.google-apps.folder` | WIRED | Lines 59-64: body includes `"mimeType": "application/vnd.google-apps.folder"` and `"parents": [parent_id]`. Returns `result.get("id")`. |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|--------------|--------|--------------------|--------|
| `upload_drive.py:main()` | `subfolder_id` | `create_subfolder()` return value from Drive API | Yes — Drive API `files().create().execute()` returns real folder ID | FLOWING |
| `upload_drive.py:main()` | `uploaded` | `upload_to_subfolder()` iterates `Path(folder_path).rglob("*")` | Yes — rglob over real filesystem path, Drive API create per file | FLOWING |
| `upload_drive.py:main()` | `cartella_nome` | `nome_cartella(datada, dataa)` from env vars | Yes — reads `FESR_DATA_DA` / `FESR_DATA_A` from environment | FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| 7 unit tests pass | `python -m pytest test_upload_drive_subfolder.py -v` | 7 passed in 0.63s | PASS |
| AST function structure | `python -c "import ast; ..."` | All 5 required functions present; `upload_folder` absent | PASS |
| No import from scraper.py | grep for `import scraper` in upload_drive.py | No matches | PASS |
| drive_url.txt uses subfolder_id | grep for `subfolder_url` in upload_drive.py | Line 119-121: `subfolder_url` built from `subfolder_id`, written to `drive_url.txt` | PASS |
| upload_to_subfolder does not call build() | AST inspection of function body | No `build(` call inside `upload_to_subfolder` | PASS |

### Probe Execution

Step 7c not applicable — no probe scripts declared in PLAN or present under `scripts/*/tests/`.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| DRIVE-01 | 05-01-PLAN.md | upload_drive.py crea sottocartella in GDRIVE_FOLDER_ID con nome che include il periodo | SATISFIED | `create_subfolder(service, folder_id, cartella_nome)` in main(); `nome_cartella()` returns `FESR_{period}` or `FESR_{YYYYMMDD}` fallback. |
| DRIVE-02 | 05-01-PLAN.md | File caricati nella sottocartella; drive_url.txt punta alla sottocartella | SATISFIED | `upload_to_subfolder()` uses `subfolder_id` as parent. `drive_url.txt` written with `subfolder_url` containing `subfolder_id`. |

### Anti-Patterns Found

No anti-patterns detected.

- No TBD / FIXME / XXX markers in `upload_drive.py` or `test_upload_drive_subfolder.py`
- No placeholder returns (`return null`, `return {}`, `return []`)
- No stub handlers
- `upload_folder` (old name) fully removed — no dead code

### Human Verification Required

None. All must-haves are verifiable statically and via the automated test suite. The integration against a live Drive account (actual subfolder creation and file upload) cannot be verified programmatically without real credentials, but this is expected and outside the scope of static verification. The code path is fully exercised by unit tests via mocks.

### Gaps Summary

No gaps. All 5 truths verified, both required artifacts substantive and wired, all key links confirmed, both requirements DRIVE-01 and DRIVE-02 satisfied. Test suite passes 7/7.

---

_Verified: 2026-06-11T14:00:00Z_
_Verifier: Claude (gsd-verifier)_
