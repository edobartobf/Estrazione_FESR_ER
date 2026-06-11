<!-- generated-by: gsd-doc-writer -->
# Testing

Guida al framework di test, ai comandi di esecuzione e alle convenzioni per scrivere nuovi test per la pipeline FESR Scraper.

## Framework e setup

Il progetto usa il framework di test standard di Python eseguendo i file di test direttamente come script (`python -m pytest` o esecuzione diretta). Non è configurato alcun framework esterno dedicato (pytest è consigliato ma non dichiarato come dipendenza obbligatoria).

I test si trovano nella root del progetto con il prefisso `test_`. Prima di eseguire i test, assicurarsi che le dipendenze siano installate:

```bash
pip install requests beautifulsoup4 google-auth google-auth-oauthlib google-api-python-client
```

## Eseguire i test

### Tutti i test (con pytest)

```bash
pytest test_applysecrets_pdf_flags.py test_upload_drive_subfolder.py -v
```

### Singolo file di test

```bash
python test_applysecrets_pdf_flags.py
python test_upload_drive_subfolder.py
```

### Verifica integrità workflow YAML

```bash
python verify_04_02.py
```

Questo script verifica che il file `.github/workflows/fesr_scraper.yml` contenga le variabili d'ambiente `FESR_SCARICA_LINK_PDF` e `FESR_SCARICA_PDF` impostate a `true` nel passo `Esegui scraper`.

## File di test esistenti

| File | Modulo testato | Descrizione |
|---|---|---|
| `test_applysecrets_pdf_flags.py` | `scraper.py` — funzione `applysecrets()` | Verifica il parsing delle env var `FESR_SCARICA_LINK_PDF` e `FESR_SCARICA_PDF` |
| `test_upload_drive_subfolder.py` | `upload_drive.py` — funzioni `datesuffix()` e `nome_cartella()` | Verifica la generazione del suffisso data e del nome cartella Google Drive |

### test_applysecrets_pdf_flags.py — 6 test

| Test | Comportamento verificato |
|---|---|
| `test_scarica_link_pdf_true` | `FESR_SCARICA_LINK_PDF=true` → `SCARICA_LINK_PDF` diventa `True` |
| `test_scarica_pdf_1` | `FESR_SCARICA_PDF=1` → `SCARICA_PDF` e `SCARICA_LINK_PDF` entrambi `True` |
| `test_scarica_pdf_implies_link_pdf` | `FESR_SCARICA_PDF=true` senza `FESR_SCARICA_LINK_PDF` → entrambi `True` (implicazione prerequisito) |
| `test_no_env_vars_remain_false` | Nessuna env var impostata → entrambi i flag rimangono `False` |
| `test_scarica_link_pdf_yes` | `FESR_SCARICA_LINK_PDF=yes` → `SCARICA_LINK_PDF` diventa `True` |
| `test_scarica_link_pdf_false_string` | `FESR_SCARICA_LINK_PDF=false` → `SCARICA_LINK_PDF` rimane `False` |

### test_upload_drive_subfolder.py — 7 test

| Test | Comportamento verificato |
|---|---|
| `test_datesuffix_both_dates` | Entrambe le date → suffisso `04giu_10giu` |
| `test_datesuffix_only_da` | Solo data da → suffisso `04giu` |
| `test_datesuffix_only_a` | Solo data a → suffisso `10giu` |
| `test_datesuffix_both_none` | Nessuna data → stringa vuota |
| `test_nome_cartella_both_dates` | Entrambe le date → `FESR_04giu_10giu` |
| `test_nome_cartella_none_none_uses_today` | Nessuna data → `FESR_YYYYMMDD` con data odierna (mock) |
| `test_nome_cartella_only_da` | Solo data da → `FESR_04giu` |

## Scrivere nuovi test

### Convenzioni di naming

- I file di test usano il prefisso `test_` seguito dal modulo o funzionalità testata (es. `test_applysecrets_pdf_flags.py`).
- Le funzioni di test usano il prefisso `test_` seguito da una descrizione del comportamento atteso.
- I file di test si trovano nella root del progetto insieme ai moduli testati.

### Pattern per il mocking

Per isolare componenti che dipendono da risorse esterne (Google Drive, SMTP, file system), usare `unittest.mock`:

```python
from unittest.mock import patch
from datetime import date

# Mock della data corrente
with patch("upload_drive.date") as mock_date:
    mock_date.today.return_value = date(2026, 6, 11)
    result = nome_cartella(None, None)
assert result == "FESR_20260611"
```

### Pattern per le variabili d'ambiente

Per testare funzioni che leggono variabili d'ambiente, pulire lo stato prima e dopo ogni test:

```python
import os

def _clear_fesr_env():
    for key in ["FESR_SCARICA_LINK_PDF", "FESR_SCARICA_PDF"]:
        os.environ.pop(key, None)

def test_mia_funzione():
    _clear_fesr_env()
    os.environ["FESR_SCARICA_PDF"] = "true"
    # ... esegui e verifica
    _clear_fesr_env()
```

### Pattern per il reload del modulo

`scraper.py` legge variabili d'ambiente a livello di modulo tramite `applysecrets()`. Per testare diversi valori di env var nello stesso processo Python, ricaricare il modulo:

```python
import importlib, sys

def _reload_scraper():
    if "scraper" in sys.modules:
        importlib.reload(sys.modules["scraper"])
        return sys.modules["scraper"]
    else:
        import scraper
        return scraper
```

## Coverage

No coverage threshold configured. Non è presente alcuna configurazione di soglie minime di copertura (`pytest-cov`, `.coveragerc`, o simili).

Per generare un report di copertura manualmente:

```bash
pip install pytest-cov
pytest test_applysecrets_pdf_flags.py test_upload_drive_subfolder.py --cov=scraper --cov=upload_drive --cov-report=term-missing
```

## Integrazione CI

I test vengono eseguiti nel workflow GitHub Actions **FESR Scraper** (`.github/workflows/fesr_scraper.yml`).

**Attenzione:** il workflow attuale non include un passo dedicato all'esecuzione dei test automatici — il job `scrape` esegue direttamente `python scraper.py`. Per aggiungere un passo di test al workflow, inserire prima del passo `Esegui scraper`:

```yaml
- name: Esegui test unitari
  run: python -m pytest test_applysecrets_pdf_flags.py test_upload_drive_subfolder.py -v
```

Il workflow è attivato da:
- Schedule: ogni lunedì alle 06:00 UTC
- `workflow_dispatch`: trigger manuale da GitHub UI
