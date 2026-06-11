<!-- generated-by: gsd-doc-writer -->
# Deployment

Questa guida descrive come il progetto FESR Scraper viene eseguito in produzione tramite GitHub Actions, come configurare i secret necessari, e come ripristinare un'esecuzione in caso di errore.

---

## Target di deployment

Il progetto non richiede infrastruttura server dedicata. L'unico target di esecuzione è **GitHub Actions** su runner `ubuntu-latest`.

| Target | File di configurazione |
|--------|------------------------|
| GitHub Actions (CI/CD) | `.github/workflows/fesr_scraper.yml` |

Non sono presenti `Dockerfile`, `docker-compose.yml`, o configurazioni per piattaforme cloud (Vercel, Fly.io, Railway, ecc.).

---

## Pipeline CI/CD

### Trigger

Il workflow `FESR Scraper` si attiva in due modi:

1. **Automatico (schedule)** — Ogni lunedì alle 06:00 UTC tramite cron `0 6 * * 1`.
2. **Manuale (workflow_dispatch)** — Avviabile dalla tab Actions del repository con parametri opzionali:

| Parametro | Descrizione | Default |
|-----------|-------------|---------|
| `keyword` | Parola chiave di ricerca (vuoto = tutto) | `""` |
| `data_da` | Data di inizio periodo `DD/MM/YYYY` (vuoto = automatico) | calcolato |
| `data_a` | Data di fine periodo `DD/MM/YYYY` (vuoto = automatico) | calcolato |
| `solo_delibere` | Filtra solo Delibere di Giunta | `"true"` |

### Sequenza dei passi

1. **Checkout repository** — `actions/checkout@v4`
2. **Setup Python** — `actions/setup-python@v5` con Python `3.11`
3. **Installa dipendenze** — `pip install requests beautifulsoup4 google-auth google-auth-oauthlib google-api-python-client`
4. **Calcola periodo** — Script inline che determina `FESR_DATA_DA` e `FESR_DATA_A`; se non forniti manualmente, usa la settimana precedente (lunedì–domenica).
5. **Esegui scraper** — `python scraper.py` con PDF download abilitato (`FESR_SCARICA_LINK_PDF=true`, `FESR_SCARICA_PDF=true`).
6. **Carica output come artifact** — I file in `data/` sono allegati all'esecuzione con nome `fesr-output-{run_id}` (retention GitHub predefinita: 90 giorni). <!-- VERIFY: artifact retention period configured in GitHub repository settings -->
7. **Verifica secret disponibili** — Controlla la presenza di `GDRIVE_REFRESH_TOKEN` e `SMTP_HOST`; i passi successivi sono condizionali.
8. **Carica su Google Drive** *(condizionale, se `GDRIVE_REFRESH_TOKEN` è configurato)* — `python upload_drive.py`
9. **Invia email di riepilogo** *(condizionale, se `SMTP_HOST` è configurato)* — `python notify_email.py`

---

## Configurazione dei secret

Tutti i valori sensibili sono iniettati tramite **GitHub Secrets** del repository. Impostarli in: `Settings → Secrets and variables → Actions → New repository secret`.

### Secret Google Drive

Richiesti da `upload_drive.py`. Il passo viene saltato se `GDRIVE_REFRESH_TOKEN` è assente.

| Secret | Obbligatorio | Descrizione |
|--------|:------------:|-------------|
| `GDRIVE_CLIENT_ID` | Sì | Client ID dell'applicazione OAuth2 su Google Cloud Console. |
| `GDRIVE_CLIENT_SECRET` | Sì | Client Secret dell'applicazione OAuth2. |
| `GDRIVE_REFRESH_TOKEN` | Sì | Refresh token OAuth2 con scope `drive.file`. Generato una volta; rinnovato automaticamente dallo script. |
| `GDRIVE_FOLDER_ID` | Sì | ID della cartella Drive di destinazione (visibile nell'URL su `drive.google.com`). |

### Secret SMTP

Richiesti da `notify_email.py`. Il passo viene saltato se `SMTP_HOST` è assente.

| Secret | Obbligatorio | Note |
|--------|:------------:|------|
| `SMTP_HOST` | Sì | Hostname del server SMTP. |
| `SMTP_PORT` | No | Default `587` (STARTTLS). |
| `SMTP_USER` | Sì | Indirizzo email del mittente. |
| `SMTP_PASS` | Sì | Password SMTP o App Password. |
| `EMAIL_RECIPIENTS` | Sì | Lista destinatari separati da virgola. |

Per il dettaglio completo delle variabili d'ambiente vedere [CONFIGURATION.md](CONFIGURATION.md).

---

## Setup iniziale

Prima della prima esecuzione automatica:

1. Creare un'applicazione OAuth2 su [Google Cloud Console](https://console.cloud.google.com/) con scope `https://www.googleapis.com/auth/drive.file`. <!-- VERIFY: exact Google Cloud Console project and OAuth consent screen configuration -->
2. Generare il refresh token OAuth2 eseguendo il flusso di autorizzazione una sola volta in locale.
3. Creare la cartella di destinazione su Google Drive e copiarne l'ID dall'URL.
4. Aggiungere tutti i secret elencati sopra nelle impostazioni del repository GitHub.
5. (Opzionale) Eseguire un dispatch manuale dalla tab Actions per verificare il funzionamento prima del primo schedule automatico.

---

## Procedura di rollback

Non esiste un meccanismo di rollback automatico configurato nel workflow. In caso di esecuzione anomala:

1. **Ripristino dati** — Scaricare l'artifact `fesr-output-{run_id}` dell'ultima esecuzione riuscita dalla tab Actions.
2. **Rimozione file Drive errati** — Eliminare manualmente la cartella `FESR_{date_suffix}` caricata per errore dalla cartella Drive di destinazione. <!-- VERIFY: whether Drive upload creates subfolders or uploads flat files -->
3. **Riesecuzione manuale** — Avviare un nuovo workflow dispatch specificando il periodo corretto nei campi `data_da` e `data_a` (formato `DD/MM/YYYY`).
4. **Rollback del codice** — In caso di regressione del codice, fare il revert del commit problematico e fare push su `main`; il prossimo schedule userà il codice ripristinato.

---

## Monitoraggio

Non sono integrate librerie di application monitoring (Sentry, Datadog, ecc.).

Il monitoraggio dell'esecuzione avviene tramite gli strumenti nativi di GitHub Actions:

- **Log delle esecuzioni** — Visibili nella tab Actions del repository per ogni run.
- **Email di notifica GitHub** — GitHub invia automaticamente un'email al proprietario del repository in caso di workflow fallito. <!-- VERIFY: GitHub notification settings for the repository owner -->
- **Email di riepilogo applicativa** — `notify_email.py` invia ai destinatari in `EMAIL_RECIPIENTS` un report con il numero di delibere trovate e le azioni FESR rilevate, allegando i CSV prodotti.
