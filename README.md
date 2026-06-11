# Estrazione delibere Emilia-Romagna

Pipeline per cercare le delibere regionali dal portale SIIR della Regione Emilia-Romagna e ricostruire l'uso del FESR.

## Uso rapido da VS Code

Apri `scraper.py`, modifica solo le variabili nella sezione iniziale e premi **Run Python File**.

Per scaricare tutto il FESR 2026, CSV e PDF, lascia:

```python
ANNI = "2026"
SCARICA_LINK_PDF = True
SCARICA_PDF = True
MAX_PAGINE = None
MAX_PDF = None
```

Puoi usare anche un range:

```python
ANNI = "2023-2026"
```

oppure una lista precisa:

```python
ANNI = ["2026", "2025", "2023"]
```

Per filtrare per periodo specifico:

```python
DATA_DA = "01/01/2026"
DATA_A = "31/03/2026"
```

Output principali:

- `data/delibere_2026.csv`: tutte le righe trovate, con campi normalizzati.
- `data/delibere_2026.json`: stesso contenuto in JSON.
- `data/riepilogo_azioni_2026.csv`: conteggio per azione FESR.
- `data/riepilogo_manovre_2026.csv`: conteggio per tipo di manovra.
- `data/riepilogo_beneficiari_2026.csv`: primi beneficiari ricavati dall'oggetto.
- `data/pdf/`: PDF delle delibere (se `SCARICA_PDF = True`).

La cartella `data/` e' ignorata da Git: contiene output rigenerabili, inclusi eventuali PDF.

Ricalcolare i riepiloghi da un CSV gia' scaricato:

```bash
python3 analisi.py data/delibere_2026.csv
```

## Automazione GitHub Actions

Il workflow `.github/workflows/fesr_scraper.yml` esegue lo scraping ogni lunedi' mattina (cron) e ad ogni `workflow_dispatch` manuale.

Ad ogni run:
1. Scarica tutte le delibere della settimana precedente (DATA_DA / DATA_A calcolati automaticamente).
2. Scarica i PDF delle delibere (`FESR_SCARICA_PDF=true`, `FESR_SCARICA_LINK_PDF=true`).
3. Carica CSV riassuntivo + PDF in una sottocartella Google Drive denominata con il periodo, es. `FESR_04giu_10giu`.
4. Invia un'email di riepilogo con link diretto alla sottocartella Drive.

Il `workflow_dispatch` non ha keyword predefinita: scarica tutte le delibere del periodo senza filtro.

### Secrets richiesti

| Secret | Descrizione |
|--------|-------------|
| `FESR_GDRIVE_FOLDER_ID` | ID cartella root su Google Drive |
| `FESR_OAUTH2_CLIENT_ID` | OAuth2 client ID per Drive |
| `FESR_OAUTH2_CLIENT_SECRET` | OAuth2 client secret |
| `FESR_OAUTH2_REFRESH_TOKEN` | OAuth2 refresh token |
| `FESR_SMTP_HOST` | Host SMTP per email di riepilogo |
| `FESR_SMTP_PORT` | Porta SMTP |
| `FESR_SMTP_USER` | Username SMTP |
| `FESR_SMTP_PASSWORD` | Password SMTP |
| `FESR_EMAIL_FROM` | Mittente email |
| `FESR_EMAIL_TO` | Destinatario email |

## Upload su Google Drive

`upload_drive.py` gestisce l'upload OAuth2. Ad ogni esecuzione:
- Crea una sottocartella in `GDRIVE_FOLDER_ID` con nome `FESR_<data_da>_<data_a>`.
- Carica CSV riassuntivo e tutti i PDF presenti in `data/pdf/`.
- Scrive `data/drive_url.txt` con il link diretto alla sottocartella.

## Note

Il portale restituisce 10 risultati per pagina anche quando viene chiesta una dimensione maggiore. Lo scraper segue quindi la paginazione generata dal sito.

## Pubblicazione su GitHub

Dopo aver creato un repository vuoto su GitHub:

```bash
git remote add origin https://github.com/NOME_UTENTE/NOME_REPO.git
git push -u origin main
```

## Installazione

Requisiti: Python 3 con pip.

```bash
pip install -r requirements.txt
```

Dipendenze installate: `requests>=2.31.0`, `beautifulsoup4>=4.12.0`.

## Test

```bash
python -m pytest test_applysecrets_pdf_flags.py test_upload_drive_subfolder.py
```

- `test_applysecrets_pdf_flags.py`: verifica il parsing delle variabili d'ambiente `FESR_SCARICA_LINK_PDF` e `FESR_SCARICA_PDF` in `applysecrets()`.
- `test_upload_drive_subfolder.py`: verifica la creazione della sottocartella su Google Drive in `upload_drive.py`.
