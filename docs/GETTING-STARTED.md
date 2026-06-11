<!-- generated-by: gsd-doc-writer -->
# Guida introduttiva

Questa guida descrive i prerequisiti, l'installazione e la prima esecuzione del progetto FESR Scraper.

---

## Prerequisiti

- **Python >= 3.8** — verificare con `python --version` o `python3 --version`
- **pip** — incluso con le versioni standard di Python
- Connessione internet per accedere al portale SIIR della Regione Emilia-Romagna

Non sono richiesti account o credenziali per l'esecuzione locale di base (lo scraping del portale pubblico non richiede autenticazione). Le credenziali Google Drive e SMTP sono necessarie solo per l'automazione via GitHub Actions — vedere docs/CONFIGURATION.md.

---

## Installazione

1. Clona il repository:

```bash
git clone https://github.com/NOME_UTENTE/NOME_REPO.git
cd Estrazione_FESR_ER
```

2. Installa le dipendenze:

```bash
pip install -r requirements.txt
```

Le dipendenze installate sono `requests>=2.31.0` e `beautifulsoup4>=4.12.0`.

---

## Prima esecuzione

1. Apri `scraper.py` e verifica le variabili nella sezione iniziale. I valori predefiniti eseguono uno scraping dell'anno 2026 senza scaricare PDF:

```python
ANNI = "2026"
KEYWORD = ""
SCARICA_LINK_PDF = False
SCARICA_PDF = False
MAX_PAGINE = None
MAX_PDF = None
```

2. Esegui lo script:

```bash
python scraper.py
```

oppure, da VS Code, apri `scraper.py` e premi **Run Python File**.

3. Al termine troverai nella cartella `data/` i file CSV e JSON con le delibere trovate:

```
data/delibere_2026.csv
data/delibere_2026.json
data/riepilogo_azioni_2026.csv
data/riepilogo_manovre_2026.csv
data/riepilogo_beneficiari_2026.csv
```

La cartella `data/` è ignorata da Git: i file generati non vengono committati.

---

## Problemi comuni

**Python non trovato o versione errata**
Su alcuni sistemi il comando è `python3` invece di `python`. Se `python --version` restituisce Python 2.x, usare esplicitamente `python3 scraper.py` e `pip3 install -r requirements.txt`.

**ModuleNotFoundError: No module named 'bs4' o 'requests'**
Le dipendenze non sono state installate nell'ambiente corretto. Se si usa un virtual environment, assicurarsi di attivarlo prima di eseguire `pip install -r requirements.txt`:

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
# oppure
source .venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
```

**Timeout o errori di connessione al portale SIIR**
Il portale potrebbe essere temporaneamente non raggiungibile. Riprovare dopo qualche minuto. Per ridurre il rischio di rate limiting è possibile aumentare `PAUSA_SECONDI` in `scraper.py` (valore predefinito: `0.4` secondi).

**La cartella `data/` non viene creata**
Viene creata automaticamente dallo script alla prima esecuzione. Se persiste il problema, verificare i permessi di scrittura nella directory del progetto.

---

## Passi successivi

- **Configurazione avanzata** (anni, filtri per data, download PDF, keyword): vedere [docs/CONFIGURATION.md](CONFIGURATION.md).
- **Architettura e moduli**: vedere [docs/ARCHITECTURE.md](ARCHITECTURE.md).
- **Automazione settimanale con GitHub Actions**: vedere la sezione "Automazione GitHub Actions" nel [README.md](../README.md).
- **Eseguire i test**: `python -m pytest test_applysecrets_pdf_flags.py test_upload_drive_subfolder.py`
