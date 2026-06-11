<!-- generated-by: gsd-doc-writer -->
# Configurazione

Questa guida descrive tutte le variabili di configurazione del progetto FESR Scraper, suddivise per contesto d'uso: esecuzione locale tramite `scraper.py` e esecuzione automatica tramite GitHub Actions.

---

## Variabili locali (scraper.py)

Le variabili di configurazione per l'esecuzione locale sono definite direttamente in cima a `scraper.py`. Modificarle prima di eseguire lo script.

| Variabile | Tipo | Default | Descrizione |
|-----------|------|---------|-------------|
| `ANNI` | `str` o `list` | `"2026"` | Anno o intervallo di anni da scaricare. Formati accettati: singolo anno `"2026"`, intervallo `"2023-2026"`, lista `["2026", "2025"]`. |
| `KEYWORD` | `str` | `""` | Parola chiave per filtrare le delibere nel campo oggetto. Stringa vuota scarica tutte le delibere senza filtro. |
| `CARTELLA_OUTPUT` | `str` | `"data"` | Percorso della cartella in cui salvare CSV, JSON e PDF generati. Viene creata automaticamente se non esiste. |
| `SCARICA_LINK_PDF` | `bool` | `False` | Se `True`, risolve il link diretto al PDF per ogni delibera visitando la pagina di dettaglio. Necessario per `SCARICA_PDF`. |
| `SCARICA_PDF` | `bool` | `False` | Se `True`, scarica fisicamente i file PDF nella sottocartella `pdf/` di `CARTELLA_OUTPUT`. Attiva automaticamente `SCARICA_LINK_PDF`. |
| `MAX_PAGINE` | `int` o `None` | `None` | Limita il numero di pagine di risultati da elaborare. `None` scarica tutte le pagine disponibili. |
| `MAX_PDF` | `int` o `None` | `None` | Limita il numero di PDF da scaricare per esecuzione. `None` scarica tutti i PDF trovati. |
| `PAUSA_SECONDI` | `float` | `0.4` | Pausa in secondi tra una richiesta HTTP e la successiva, per non sovraccaricare il portale SIIR. |
| `TIMEOUT_SECONDI` | `int` | `30` | Timeout in secondi per ogni singola richiesta HTTP. |
| `DATA_DA` | `str` o `None` | `None` | Data di inizio del filtro per periodo, nel formato `DD/MM/YYYY`. Esempio: `"04/06/2026"`. |
| `DATA_A` | `str` o `None` | `None` | Data di fine del filtro per periodo, nel formato `DD/MM/YYYY`. Esempio: `"11/06/2026"`. |

### Dipendenza tra SCARICA_LINK_PDF e SCARICA_PDF

Se `SCARICA_PDF = True` e `SCARICA_LINK_PDF = False`, lo script forza automaticamente `SCARICA_LINK_PDF = True` perché i link sono un prerequisito fisico del download. Un avviso viene stampato a console in questo caso.

---

## Variabili d'ambiente

Tutte le variabili locali di `scraper.py` possono essere sovrascritte tramite variabili d'ambiente, senza modificare il codice. Questo meccanismo è usato da GitHub Actions e può essere usato anche in ambienti di staging o CI locali.

### Variabili d'ambiente dello scraper

| Variabile d'ambiente | Sovrascrive | Tipo | Note |
|----------------------|-------------|------|------|
| `FESR_KEYWORD` | `KEYWORD` | `str` | Stringa vuota equivale a nessun filtro. |
| `FESR_ANNI` | `ANNI` | `str` | Accetta gli stessi formati della variabile locale. |
| `FESR_DATA_DA` | `DATA_DA` | `str` | Formato richiesto: `DD/MM/YYYY`. Stringa vuota viene trattata come `None`. |
| `FESR_DATA_A` | `DATA_A` | `str` | Formato richiesto: `DD/MM/YYYY`. Stringa vuota viene trattata come `None`. |
| `FESR_SCARICA_LINK_PDF` | `SCARICA_LINK_PDF` | `str` | Valori accettati: `true`, `1`, `yes` (case-insensitive). Qualsiasi altro valore non vuoto equivale a `False`. |
| `FESR_SCARICA_PDF` | `SCARICA_PDF` | `str` | Valori accettati: `true`, `1`, `yes` (case-insensitive). |
| `FESR_OUTPUT` | `CARTELLA_OUTPUT` | `str` | Usato anche da `upload_drive.py` e `notify_email.py`. Default: `data`. |

### Variabili d'ambiente di Google Drive

Richieste da `upload_drive.py`. Tutte e quattro sono obbligatorie; lo script termina con errore se una qualsiasi manca.

| Variabile d'ambiente | Obbligatoria | Descrizione |
|----------------------|:------------:|-------------|
| `GDRIVE_CLIENT_ID` | Sì | Client ID dell'applicazione OAuth2 registrata su Google Cloud Console. |
| `GDRIVE_CLIENT_SECRET` | Sì | Client Secret dell'applicazione OAuth2. |
| `GDRIVE_REFRESH_TOKEN` | Sì | Refresh token OAuth2 con scope `https://www.googleapis.com/auth/drive.file`. Usato per rinnovare automaticamente l'access token. |
| `GDRIVE_FOLDER_ID` | Sì | ID della cartella Google Drive di destinazione (visibile nell'URL della cartella su drive.google.com). |

### Variabili d'ambiente SMTP

Richieste da `notify_email.py`. `SMTP_HOST`, `SMTP_USER`, `SMTP_PASS` e `EMAIL_RECIPIENTS` sono obbligatorie; `SMTP_PORT` è opzionale.

| Variabile d'ambiente | Obbligatoria | Default | Descrizione |
|----------------------|:------------:|---------|-------------|
| `SMTP_HOST` | Sì | — | Hostname del server SMTP. |
| `SMTP_PORT` | No | `587` | Porta del server SMTP. La connessione usa STARTTLS. |
| `SMTP_USER` | Sì | — | Username SMTP (indirizzo email del mittente). |
| `SMTP_PASS` | Sì | — | Password SMTP o App Password. |
| `EMAIL_RECIPIENTS` | Sì | — | Lista di destinatari separati da virgola. Esempio: `utente1@example.com,utente2@example.com`. |

---

## Impostazioni per ambiente

### Esecuzione locale (sviluppo/test)

Modifica le variabili direttamente in `scraper.py`. Configurazione consigliata per un test rapido:

```python
ANNI = "2026"
KEYWORD = "FESR"
SCARICA_LINK_PDF = False
SCARICA_PDF = False
MAX_PAGINE = 2
MAX_PDF = None
```

### GitHub Actions (automazione settimanale)

Il workflow `.github/workflows/fesr_scraper.yml` si attiva ogni lunedì alle 06:00 UTC e imposta automaticamente il periodo sulla settimana precedente (da lunedì a domenica). I valori fissi usati in CI sono:

```
FESR_SCARICA_LINK_PDF = true
FESR_SCARICA_PDF      = true
FESR_OUTPUT           = data
```

Le credenziali Drive e SMTP vengono iniettate dai GitHub Secrets del repository. Il workflow salta i passi `upload_drive.py` e `notify_email.py` se i rispettivi secret non sono configurati.

#### Secret GitHub da configurare

| Secret | Modulo che lo usa |
|--------|-------------------|
| `GDRIVE_CLIENT_ID` | `upload_drive.py` |
| `GDRIVE_CLIENT_SECRET` | `upload_drive.py` |
| `GDRIVE_REFRESH_TOKEN` | `upload_drive.py` |
| `GDRIVE_FOLDER_ID` | `upload_drive.py` |
| `SMTP_HOST` | `notify_email.py` |
| `SMTP_PORT` | `notify_email.py` |
| `SMTP_USER` | `notify_email.py` |
| `SMTP_PASS` | `notify_email.py` |
| `EMAIL_RECIPIENTS` | `notify_email.py` |

---

## Formato delle date

Tutte le date fornite tramite `DATA_DA`, `DATA_A`, `FESR_DATA_DA`, `FESR_DATA_A` devono rispettare il formato `DD/MM/YYYY` (giorno/mese/anno a quattro cifre). Lo script solleva `ValueError` se il formato non è corretto.

Esempi validi:
- `"04/06/2026"` — 4 giugno 2026
- `"01/01/2023"` — 1 gennaio 2023

---

## Formato degli output

I file generati dallo scraper vengono salvati in `CARTELLA_OUTPUT` (default: `data/`).

| Tipo file | Naming convention | Esempio |
|-----------|-------------------|---------|
| CSV delibere | `delibere_{anno}_{keyword}.csv` | `delibere_2026_.csv` |
| JSON delibere | `delibere_{anno}_{keyword}.json` | `delibere_2026_.json` |
| Riepilogo azioni | `riepilogo_azioni_{suffix}.csv` | `riepilogo_azioni_2026_.csv` |
| Riepilogo manovre | `riepilogo_manovre_{suffix}.csv` | — |
| Riepilogo beneficiari | `riepilogo_beneficiari_{suffix}.csv` | — |
| Riepilogo proponenti | `riepilogo_proponenti_{suffix}.csv` | — |
| PDF delibere | `data/pdf/{nome_originale}.pdf` | — |

Quando si usa il filtro per periodo, il suffix include le date in formato abbreviato (es. `04giu_11giu`). Quando si scaricano più anni, viene generato un file aggregato `delibere_{anno_inizio}_{anno_fine}_{keyword}_tutti_gli_anni.csv`.
