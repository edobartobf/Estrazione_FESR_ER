# Estrazione delibere Emilia-Romagna

Pipeline per cercare le delibere regionali dal portale SIIR della Regione Emilia-Romagna e ricostruire l'uso del FESR.

## Uso rapido da VS Code

Apri `scraper.py`, modifica solo le variabili nella sezione iniziale e premi **Run Python File**.

Per scaricare tutto il FESR 2026, CSV e PDF, lascia:

```python
ANNI = "2026"
KEYWORD = "FESR"
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

Output principali:

- `data/delibere_2026_fesr.csv`: tutte le righe trovate, con campi normalizzati.
- `data/delibere_2026_fesr.json`: stesso contenuto in JSON.
- `data/riepilogo_azioni_2026_fesr.csv`: conteggio per azione FESR.
- `data/riepilogo_manovre_2026_fesr.csv`: conteggio per tipo di manovra.
- `data/riepilogo_beneficiari_2026_fesr.csv`: primi beneficiari ricavati dall'oggetto.

La cartella `data/` e' ignorata da Git: contiene output rigenerabili, inclusi eventuali PDF.

Ricalcolare i riepiloghi da un CSV gia' scaricato:

```bash
python3 analisi.py data/delibere_2026_fesr.csv
```

## Note

Il portale restituisce 10 risultati per pagina anche quando viene chiesta una dimensione maggiore. Lo scraper segue quindi la paginazione generata dal sito.

## Pubblicazione su GitHub

Dopo aver creato un repository vuoto su GitHub:

```bash
git remote add origin https://github.com/NOME_UTENTE/NOME_REPO.git
git push -u origin main
```
