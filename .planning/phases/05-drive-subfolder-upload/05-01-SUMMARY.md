---
phase: 05-drive-subfolder-upload
plan: "01"
subsystem: infra
tags: [google-drive, oauth2, python, upload, subfolder]

requires:
  - phase: 04-pdf-download
    provides: PDF files in data/ folder ready for upload

provides:
  - datesuffix() standalone in upload_drive.py (Italian month abbreviations, DD/MM/YYYY input)
  - nome_cartella() fallback to FESR_YYYYMMDD when dates absent
  - create_subfolder(service, parent_id, name) creates Drive folder via files.create
  - upload_to_subfolder(folder_path, subfolder_id, service) uploads recursively to subfolder
  - main() creates dated subfolder then uploads all files there; drive_url.txt points to subfolder

affects: [notify_email, fesr_scraper_yml]

tech-stack:
  added: []
  patterns:
    - "Subfolder Drive creata via files.create con mimeType application/vnd.google-apps.folder"
    - "datesuffix() duplicato inline in upload_drive.py — nessun import cross-script"
    - "Service OAuth2 costruito una volta in main() e passato alle funzioni"

key-files:
  created: [test_upload_drive_subfolder.py]
  modified: [upload_drive.py]

key-decisions:
  - "datesuffix() duplicated inline (not imported from scraper.py) to keep scripts independent"
  - "Service object built once in main() then passed to create_subfolder() and upload_to_subfolder() — avoids double token refresh"
  - "drive_url.txt now contains subfolder URL — downstream notify_email.py needs no changes"

patterns-established:
  - "Subfolder Drive creata via files.create con mimeType application/vnd.google-apps.folder"
  - "datesuffix() duplicato inline in upload_drive.py — nessun import cross-script"
  - "Service OAuth2 costruito una volta in main() e passato alle funzioni"

requirements-completed: [DRIVE-01, DRIVE-02]

duration: 15min
completed: "2026-06-11"
---

# Phase 5 Plan 01: Drive Subfolder Upload Summary

**upload_drive.py refactored to create a dated Drive subfolder per run using datesuffix() logic (Italian months) and upload all files there; drive_url.txt now points to the subfolder**

## Performance

- **Duration:** 15 min
- **Started:** 2026-06-11T13:00:00Z
- **Completed:** 2026-06-11T13:15:00Z
- **Tasks:** 2 (Task 1 TDD: 3 commits; Task 2: 1 commit)
- **Files modified:** 2

## Accomplishments

- TDD cycle (RED/GREEN) for datesuffix() and nome_cartella() — 7 tests, all passing
- create_subfolder() function creates Drive folder via files.create with folder mimeType
- upload_to_subfolder() replaces upload_folder() — accepts pre-built service, no internal build()
- main() orchestrates: build service once, derive folder name from FESR_DATA_DA/FESR_DATA_A, create subfolder, upload all files, write subfolder URL to drive_url.txt

## Task Commits

Each task was committed atomically:

1. **Task 1 RED — Failing tests for datesuffix and folder naming** - `c747d89` (test)
2. **Task 1 GREEN — datesuffix() and nome_cartella() added** - `14456f4` (feat)
3. **Task 2 — create_subfolder(), upload_to_subfolder(), main() updated** - `423b6fe` (feat)

## Files Created/Modified

- `test_upload_drive_subfolder.py` - 7 unit tests for datesuffix() and nome_cartella() logic
- `upload_drive.py` - Refactored with datesuffix, nome_cartella, create_subfolder, upload_to_subfolder; main() updated for subfolder-first upload flow

## Decisions Made

- datesuffix() logic duplicated inline (not imported from scraper.py) — keeps upload_drive.py fully standalone
- Service object built once in main() and passed to helper functions — avoids double OAuth2 refresh
- drive_url.txt continues as the interface to notify_email.py; its content changes from root folder URL to subfolder URL — no downstream code change needed

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None - multiline Python AST check had a PowerShell quoting issue when run inline; used separate pytest invocation instead. Static structure verified via single-line python -c call.

## User Setup Required

None - no external service configuration required. All Drive secrets (GDRIVE_CLIENT_ID, GDRIVE_CLIENT_SECRET, GDRIVE_REFRESH_TOKEN, GDRIVE_FOLDER_ID) already configured in GitHub Secrets from v1.0.

## Next Phase Readiness

- DRIVE-01 and DRIVE-02 requirements satisfied
- upload_drive.py ready for the next automated run; fesr_scraper.yml "Carica su Drive" step already passes FESR_DATA_DA/FESR_DATA_A via GITHUB_ENV — no workflow changes needed
- No blockers

---
*Phase: 05-drive-subfolder-upload*
*Completed: 2026-06-11*
