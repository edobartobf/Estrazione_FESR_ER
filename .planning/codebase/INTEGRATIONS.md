# External Integrations

**Analysis Date:** 2026-06-11

## APIs & External Services

**Regione Emilia-Romagna — SIIR Delibere Portal:**
- Service: `https://servizissiir.regione.emilia-romagna.it/deliberegiunta/servlet/AdapterHTTP`
- What it's used for: querying and paginating delibere (regional council resolutions)
- SDK/Client: `requests` — no official SDK, raw HTTP calls
- Auth: None — publicly accessible portal, no credentials required
- Interaction pattern:
  - Initial search: `POST` to `BASE_URL` with a form payload (year, keyword, page size)
  - Pagination: `GET` to `BASE_URL` with query parameters per page
  - Detail pages: `GET` to individual delibera detail URLs to find PDF links
  - PDF download: `GET` with `stream=True` to retrieve binary PDF content
- Response encoding: ISO-8859-1 (decoded explicitly in `delibere.py:decodehtml`)
- Rate limiting: configurable `PAUSA_SECONDI` delay (default `0.4s`) between requests, enforced via `time.sleep` in `delibere.py`
- Timeout: configurable `TIMEOUT_SECONDI` (default `30s`) on all requests
- User-Agent: spoofed as Chrome 125 on Linux (`delibere.py:HEADERS`)

**URL constants (`delibere.py`):**
- `BASE_URL = "https://servizissiir.regione.emilia-romagna.it/deliberegiunta/servlet/AdapterHTTP"`
- `BASE_DIR = "https://servizissiir.regione.emilia-romagna.it/deliberegiunta/servlet/"`

## Data Storage

**Databases:**
- None — no database is used

**File Storage (local filesystem only):**
- Output root: `data/` directory (relative to project root, gitignored)
- CSV files: `data/delibere_{anno}_{keyword}.csv` — full record exports
- JSON files: `data/delibere_{anno}_{keyword}.json` — same records as JSON
- Summary CSVs: `data/riepilogo_azioni_*.csv`, `riepilogo_manovre_*.csv`, `riepilogo_beneficiari_*.csv`, `riepilogo_proponenti_*.csv`
- PDF files: `data/pdf/{filename}.pdf` — downloaded from the portal when `SCARICA_PDF = True`
- All paths managed via `pathlib.Path` throughout `delibere.py` and `scraper.py`

**Caching:**
- None — every run re-fetches from the portal

## Authentication & Identity

**Auth Provider:** None
- The SIIR portal requires no login or API key
- No credentials of any kind are used or stored

## Monitoring & Observability

**Error Tracking:**
- None — no error tracking service integrated

**Logs:**
- Plain `print()` statements to stdout only
- Progress messages: total results found, per-page counts, completed year summaries

## CI/CD & Deployment

**Hosting:**
- Not applicable — local scripts, no server deployment

**CI Pipeline:**
- None detected

## Environment Configuration

**Required env vars:**
- None — the project uses no environment variables

**Secrets location:**
- Not applicable — no secrets required

## Webhooks & Callbacks

**Incoming:**
- None

**Outgoing:**
- None — the tool only pulls data, it does not push or notify

---

*Integration audit: 2026-06-11*
