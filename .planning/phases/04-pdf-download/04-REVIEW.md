---
phase: 04-pdf-download
reviewed: 2026-06-11T00:00:00Z
depth: standard
files_reviewed: 2
files_reviewed_list:
  - scraper.py
  - .github/workflows/fesr_scraper.yml
findings:
  critical: 1
  warning: 2
  info: 1
  total: 4
status: issues_found
---

# Phase 4: Code Review Report

**Reviewed:** 2026-06-11
**Depth:** standard
**Files Reviewed:** 2
**Status:** issues_found

## Summary

Phase 4 added env-var-driven control of `SCARICA_LINK_PDF` and `SCARICA_PDF` in `applysecrets()`, and hardwired those env vars to `"true"` in the GitHub Actions workflow. The bool-parsing logic itself is correct. However, there is one critical behavioral defect: when env var `FESR_SCARICA_LINK_PDF` is explicitly set to `"false"` but `FESR_SCARICA_PDF` is `"true"`, the prerequisite implication silently overrides the explicit `false` without any diagnostic — this is the documented intent, but the ordering creates a silent override that cannot be countered from the outside. More importantly, the unconditional hardcoding of both PDF flags in the workflow with no `workflow_dispatch` input means operators can never suppress PDF downloads on a manual run without editing the YAML.

---

## Critical Issues

### CR-01: `FESR_SCARICA_LINK_PDF=false` is silently ignored when `FESR_SCARICA_PDF=true`

**File:** `scraper.py:87-95`

**Issue:** The prerequisite implication at line 94-95 forcibly sets `SCARICA_LINK_PDF = True` after parsing both env vars. This means an operator who sets `FESR_SCARICA_LINK_PDF=false` and `FESR_SCARICA_PDF=true` gets `SCARICA_LINK_PDF=True` with no warning. While the comment says links are a physical prerequisite for download, the silent override violates the principle of least surprise and makes the env var contract misleading: setting it to `false` appears to be accepted (no error) but has no effect. In a CI context where both vars are always `"true"`, this is benign today; but it becomes a trap the moment an operator tries to audit or change behavior without reading the source.

More critically: the implication runs unconditionally using the *global* `SCARICA_PDF` value (line 94), which means it also fires when `SCARICA_PDF` is `True` from the module-level default even if `FESR_SCARICA_PDF` was never set in the environment. If the module-level default were ever changed to `True`, `SCARICA_LINK_PDF` would be forced `True` on every run regardless of any env var.

**Fix:** Apply the implication only when `FESR_SCARICA_PDF` was actually read from the environment, and emit a warning when the override happens:

```python
val_pdf = os.environ.get("FESR_SCARICA_PDF")
if val_pdf:
    SCARICA_PDF = val_pdf.strip().lower() in ("true", "1", "yes")

val_link = os.environ.get("FESR_SCARICA_LINK_PDF")
if val_link:
    SCARICA_LINK_PDF = val_link.strip().lower() in ("true", "1", "yes")

# Prerequisite implication: only enforce when SCARICA_PDF was set via env
if val_pdf and SCARICA_PDF and not SCARICA_LINK_PDF:
    print(
        "AVVISO: FESR_SCARICA_LINK_PDF forzato a true perché FESR_SCARICA_PDF=true "
        "(i link sono prerequisito del download)."
    )
    SCARICA_LINK_PDF = True
```

---

## Warnings

### WR-01: PDF download flags hardcoded in workflow with no `workflow_dispatch` override

**File:** `.github/workflows/fesr_scraper.yml:67-68`

**Issue:** `FESR_SCARICA_LINK_PDF: "true"` and `FESR_SCARICA_PDF: "true"` are hardcoded in the `env` block of the "Esegui scraper" step. The `workflow_dispatch` block defines inputs for `keyword`, `data_da`, and `data_a`, but not for the PDF download toggles. This means:

1. A manual `workflow_dispatch` run always downloads all PDFs — there is no way to trigger a metadata-only run from the GitHub UI without editing the YAML.
2. In a run with many results, unexpected large PDF batches can exhaust the job's timeout or artifact storage quota.

**Fix:** Add `workflow_dispatch` inputs and wire them through:

```yaml
workflow_dispatch:
  inputs:
    keyword:
      description: "Keyword di ricerca (default: FESR)"
      required: false
      default: "FESR"
    data_da:
      description: "Data da (DD/MM/YYYY)"
      required: false
    data_a:
      description: "Data a (DD/MM/YYYY)"
      required: false
    scarica_pdf:
      description: "Scarica i PDF (true/false)"
      required: false
      default: "true"
```

Then in the "Esegui scraper" step:
```yaml
env:
  FESR_KEYWORD: ${{ github.event.inputs.keyword || 'FESR' }}
  FESR_SCARICA_LINK_PDF: ${{ github.event.inputs.scarica_pdf || 'true' }}
  FESR_SCARICA_PDF: ${{ github.event.inputs.scarica_pdf || 'true' }}
```

### WR-02: `applysecrets()` cannot disable a flag that is `True` in the module default

**File:** `scraper.py:87-92`

**Issue:** The guard `if val:` (lines 88, 91) is falsy for an empty string but truthy for any non-empty string — including `"false"`, `"0"`, `"no"`. This means the bool parsing does execute correctly for explicit `false`-y strings. However, the guard also means that if an env var is set to an empty string `""`, the module default is silently preserved. Since the module defaults are `False` for both flags, this is currently harmless. But there is a symmetry violation: `FESR_DATA_DA` and `FESR_DATA_A` use `if val is not None:` (lines 76, 79) while the bool flags use `if val:` — an empty string is treated differently depending on which variable is being parsed. This inconsistency will confuse future maintainers.

**Fix:** Use the same guard style for all env vars, documenting the chosen semantic:

```python
# For boolean flags: empty string = unset, treat as no-op
val = os.environ.get("FESR_SCARICA_LINK_PDF")
if val is not None and val.strip():
    SCARICA_LINK_PDF = val.strip().lower() in ("true", "1", "yes")
```

---

## Info

### IN-01: Stale comment in workflow file — still references Phase 3

**File:** `.github/workflows/fesr_scraper.yml:1`

**Issue:** The comment at line 1 reads `# Aggiornato: Phase 3 — Drive Upload + Email Notification`. This was not updated when Phase 4 changes were applied, making the file header misleading.

**Fix:** Update to reflect the current state:
```yaml
# Aggiornato: Phase 4 — PDF Download abilitato in Actions
```

---

_Reviewed: 2026-06-11_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
