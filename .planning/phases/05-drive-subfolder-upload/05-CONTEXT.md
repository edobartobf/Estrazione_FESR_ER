# Phase 5: Drive Subfolder Upload — Context

**Gathered:** 2026-06-11
**Status:** Ready for planning
**Source:** Auto-generated (infrastructure phase — no discuss needed)

<domain>
## Phase Boundary

Refactoring `upload_drive.py` so each run creates a dated subfolder inside `GDRIVE_FOLDER_ID`
and uploads all files there, instead of uploading flat to the root folder.
No user-facing behavior changes; `notify_email.py` continues to read `drive_url.txt` unchanged.

</domain>

<decisions>
## Implementation Decisions

### Subfolder naming — LOCKED
- Folder name: `FESR_{datesuffix}` where `datesuffix` uses the same logic as `scraper.py`
  (Italian month abbreviations, format `DDmm_DDmm` e.g. `FESR_04giu_10giu`)
- Date inputs: `FESR_DATA_DA` and `FESR_DATA_A` env vars (same vars used by scraper.py)
- Fallback when both dates are absent: use `FESR_{YYYYMMDD}` with the current date
  (ensures every run has its own subfolder even on manual runs without date params)

### Drive API subfolder creation — LOCKED
- Use Drive API `files.create` with `mimeType: "application/vnd.google-apps.folder"` and
  `parents: [GDRIVE_FOLDER_ID]`
- Function name: `create_subfolder(service, parent_id, name)` → returns subfolder ID
- No deduplication: each run creates a new subfolder (by design — each run is independent)

### Upload target — LOCKED
- All files uploaded to the subfolder ID, not to `GDRIVE_FOLDER_ID`
- `drive_url.txt` must contain the subfolder URL:
  `https://drive.google.com/drive/folders/{subfolder_id}`
- The root `GDRIVE_FOLDER_ID` remains the parent container — users see weekly subfolders there

### upload_folder() rename — LOCKED
- Rename `upload_folder()` to `upload_to_subfolder()` for clarity
- Signature: `upload_to_subfolder(folder_path, subfolder_id, service)`
  (pass pre-built service to avoid rebuilding credentials twice)

### Claude's Discretion
- MIME type detection for uploaded files (default resumable upload is fine)
- Whether to print the subfolder name to stdout during execution

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase context
- `.planning/ROADMAP.md` — Phase 5 goal and success criteria
- `.planning/REQUIREMENTS.md` — DRIVE-01, DRIVE-02 requirements
- `.planning/STATE.md` — accumulated decisions (datesuffix convention, OAuth2 credentials pattern)

### Source files to modify
- `upload_drive.py` — current flat uploader (68 lines); understand before editing
- `scraper.py:117-130` — `datesuffix()` function to replicate (DO NOT import from scraper — duplicate the logic inline in upload_drive.py to keep scripts independent)

### Workflow
- `.github/workflows/fesr_scraper.yml` — verify `FESR_DATA_DA`/`FESR_DATA_A` are already injected
  via `GITHUB_ENV` (set by "Calcola date" step) before "Carica su Drive" step

</canonical_refs>

<specifics>
## Specific Implementation Notes

- `datesuffix()` in `upload_drive.py` must be self-contained (no import from scraper.py)
- When `FESR_DATA_DA` and `FESR_DATA_A` are both set (normal weekly run), folder name = `FESR_{datesuffix}`
- When dates are absent (manual run without dates), folder name = `FESR_{YYYYMMDD}` using today's date
- The `upload_to_subfolder` loop should mirror the current `upload_folder` loop but recurse into `data/pdf/` subdirectory automatically (rglob handles this already)

</specifics>

<deferred>
## Deferred

- Deduplication across runs (out of scope per REQUIREMENTS.md)
- Updating `fesr_scraper.yml` "Carica su Drive" step (no changes needed — it already passes FESR_DATA_DA/FESR_DATA_A via GITHUB_ENV)

</deferred>

---

*Phase: 05-drive-subfolder-upload*
*Context gathered: 2026-06-11 — auto-generated infrastructure phase*
