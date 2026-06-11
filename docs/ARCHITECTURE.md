<!-- generated-by: gsd-doc-writer -->
# Architettura

## Panoramica del sistema

Il progetto è una pipeline di scraping sincrona a singolo thread che interroga il portale SIIR della Regione Emilia-Romagna, estrae le delibere di giunta, arricchisce ogni record con campi derivati dal testo libero dell'oggetto, e produce CSV, JSON e riepiloghi aggregati. In modo opzionale scarica i PDF allegati, carica l'output su Google Drive e invia una email di riepilogo. L'esecuzione è orchestrata direttamente in `scraper.py` o automatizzata tramite GitHub Actions ogni lunedì mattina.

## Diagramma dei componenti

```
┌──────────────────────────────────────────────────────────────────┐
│                        Entry Points                              │
│                                                                  │
│  scraper.py (esecuzione interattiva / GitHub Actions)            │
│  analisi.py (CLI — rigenera riepiloghi da CSV esistente)         │
└────────────────┬─────────────────────────────────────────────────┘
                 │ importa
                 ▼
┌────────────────────────────────────────────────────────────────────┐
│                  delibere.py — libreria core                       │
│                                                                    │
│  scraperesults()   orchestrazione pagine + record                  │
│  fetchpage()       HTTP POST/GET → HTML grezzo                     │
│  parserows()       HTML → lista di dict                            │
│  enrichrecord()    campi derivati da oggetto (regex)               │
│  findpdflink()     GET pagina dettaglio → URL PDF                  │
│  downloadpdf()     download binario → data/pdf/                    │
│  writecsv()        scrittura CSV (UTF-8, BOM)                      │
│  writejson()       scrittura JSON                                  │
│  writesummaries()  quattro CSV di riepilogo aggregati              │
└────────────────────────────────┬───────────────────────────────────┘
                                 │ scrive
                                 ▼
┌────────────────────────────────────────────────────────────────────┐
│  data/  (output runtime, git-ignored)                              │
│  ├── delibere_<suffix>.csv                                         │
│  ├── delibere_<suffix>.json                                        │
│  ├── riepilogo_azioni_<suffix>.csv                                 │
│  ├── riepilogo_manovre_<suffix>.csv                                │
│  ├── riepilogo_beneficiari_<suffix>.csv                            │
│  ├── riepilogo_proponenti_<suffix>.csv                             │
│  └── pdf/  (PDF scaricati)                                         │
└────────────────────────────────────────────────────────────────────┘
                 │ (se secrets configurati)
                 ▼
┌───────────────────────────┐    ┌──────────────────────────────────┐
│  upload_drive.py          │    │  notify_email.py                 │
│  Google Drive API v3      │    │  SMTP (MIMEMultipart)            │
│  (OAuth2, refresh token)  │    │  destinatari da EMAIL_RECIPIENTS │
└───────────────────────────┘    └──────────────────────────────────┘
```

## Flusso dei dati

### Percorso principale (scraping)

1. `scraper.py:main()` chiama `applysecrets()` per sovrascrivere le variabili di configurazione con i valori degli environment variable (usato da GitHub Actions).
2. `leggianni()` converte la variabile `ANNI` (stringa, range o lista) in una lista di anni da scorrere.
3. Per ogni anno: viene chiamato `delibere.scraperesults()` con tutti i parametri di configurazione.
4. All'interno di `scraperesults()`, per ogni pagina:
   - `fetchpage()` esegue una HTTP POST (prima pagina) o GET (pagine successive) verso il portale SIIR e decodifica la risposta ISO-8859-1.
   - `parserows()` analizza l'HTML con BeautifulSoup e produce una lista di dict grezzi.
   - Per ogni record: `enrichrecord()` applica regex sull'`oggetto` per estrarre `programma`, `azioni`, `priorita`, `cup`, `dgr`, `tipo_manovra`, `beneficiario`, `importi`.
   - Se `includelinks=True`: `findpdflink()` segue l'URL di dettaglio per recuperare il link al PDF.
   - Se `download=True`: `downloadpdf()` scarica il file binario in `data/pdf/`.
   - `time.sleep(delay)` introduce una pausa tra una pagina e l'altra.
5. `scraperesults()` restituisce la lista completa dei record per quell'anno.
6. `scraper.py:main()` chiama `writecsv()`, `writejson()`, `writesummaries()` per ogni anno.
7. Se sono richiesti più anni, viene scritto anche un file CSV/JSON/riepilogo combinato con tutti i record.

### Percorso di re-analisi (`analisi.py`)

1. `analisi.py:main()` legge un CSV già prodotto con `readcsv()`.
2. Ricava `anno` e `keyword` dagli argomenti CLI o dal primo record.
3. Chiama `delibere.writesummaries()` per rigenerare i quattro CSV di riepilogo senza ripetere lo scraping.

### Percorso CI/CD (GitHub Actions)

1. Il workflow `fesr_scraper.yml` si attiva ogni lunedì alle 06:00 UTC oppure manualmente.
2. Il passo "Calcola periodo" calcola automaticamente la settimana precedente (lunedì–domenica) se le date non sono fornite manualmente.
3. `scraper.py` viene eseguito con `FESR_SCARICA_LINK_PDF=true` e `FESR_SCARICA_PDF=true`.
4. L'output viene archiviato come GitHub Actions artifact.
5. Se il secret `GDRIVE_REFRESH_TOKEN` è presente, viene eseguito `upload_drive.py`.
6. Se il secret `SMTP_HOST` è presente, viene eseguito `notify_email.py`.

## Responsabilità dei componenti

| Componente | Responsabilità | File |
|---|---|---|
| `scraper.py` | Entry point interattivo; variabili di configurazione; loop su anni; orchestrazione output | `scraper.py` |
| `analisi.py` | CLI per rigenerare i riepiloghi da un CSV esistente senza riscraping | `analisi.py` |
| `delibere.py` | Libreria core: HTTP, paginazione, parsing HTML, arricchimento, PDF, scrittura file | `delibere.py` |
| `upload_drive.py` | Caricamento dell'output su Google Drive tramite OAuth2 con refresh token | `upload_drive.py` |
| `notify_email.py` | Invio di un'email di riepilogo con i file CSV allegati tramite SMTP | `notify_email.py` |
| `data/` | Directory di output runtime; tutti i file sono generati e git-ignored | `data/` |

## Astrazioni chiave

**Record dict:**
Rappresenta una singola delibera di giunta con tutti i campi estratti e derivati. Creato da `parserows()` e arricchito da `enrichrecord()`. Lo schema canonico è definito dalla costante `FIELDNAMES` in `delibere.py` (righe 21–44). La chiave opzionale `pdf_file` viene aggiunta a runtime da `downloadpdf()`.

**`FIELDNAMES` (costante):**
Lista ordinata dei 22 campi del record. Definisce l'ordine delle colonne nei file CSV e funge da schema concordato per l'intera pipeline.

**`scraperesults()` (funzione):**
Unico punto di orchestrazione della pipeline di scraping. Apre una `requests.Session`, itera sulle pagine, e restituisce la lista completa dei record. Nessun effetto collaterale di I/O: la scrittura su disco avviene fuori da questa funzione.

## Struttura delle directory

```
C:/web/Estrazione_FESR_ER/
│
├── scraper.py            # Entry point interattivo + variabili di configurazione
├── analisi.py            # CLI per re-analisi da CSV
├── delibere.py           # Libreria core
├── upload_drive.py       # Upload Google Drive
├── notify_email.py       # Notifica email
├── get_drive_token.py    # Utility one-shot per ottenere il refresh token OAuth2
├── requirements.txt      # Dipendenze Python
│
├── data/                 # Output runtime (git-ignored)
│   ├── *.csv / *.json
│   └── pdf/
│
├── .github/
│   └── workflows/
│       └── fesr_scraper.yml  # Pipeline CI/CD settimanale
│
├── docs/                 # Documentazione tecnica del progetto
└── tests (*)             # test_applysecrets_pdf_flags.py, test_upload_drive_subfolder.py
```

## Vincoli architetturali

- **Single-threaded:** Nessun async, nessun thread worker. La pausa esplicita `time.sleep(PAUSA_SECONDI)` tra una pagina e l'altra limita la pressione sul portale SIIR.
- **Encoding:** Il portale SIIR risponde in ISO-8859-1. La funzione `decodehtml()` in `delibere.py` gestisce la conversione esplicitamente; tutti i file di output sono scritti in UTF-8.
- **Page size fissa:** Il portale ignora le dimensioni di pagina richieste e restituisce sempre 10 record per pagina. Lo scraper rispetta questo vincolo senza tentativi di override.
- **Configurazione nel sorgente:** I parametri di `scraper.py` sono variabili a livello di modulo. In ambiente CI vengono sovrascritti dalla funzione `applysecrets()` tramite environment variable; in esecuzione locale richiedono la modifica diretta del file.
- **Dipendenze unidirezionali:** `scraper.py` → `delibere.py` e `analisi.py` → `delibere.py`. Nessuna dipendenza circolare.
- **Autenticazione portale:** Nessuna. Il portale SIIR è pubblicamente accessibile; viene impostato solo un header `User-Agent` simile a un browser.

## Gestione degli errori

Nessun blocco `try/except` esplicito nel percorso principale. Le chiamate HTTP usano `.raise_for_status()`, che propaga un `HTTPError` per risposte 4xx/5xx. Qualsiasi errore di rete o di parsing termina l'intera esecuzione con traceback non gestito.

Le funzioni di regex restituiscono stringhe vuote o dict predefiniti in caso di nessun match; non vengono sollevate eccezioni per campi assenti.

## Aspetti trasversali

| Aspetto | Implementazione |
|---|---|
| Logging | `print()` verso stdout; nessun framework di logging strutturato |
| Validazione input | Assente oltre alle assunzioni implicite sulla struttura HTML del portale |
| Throttling | `time.sleep(PAUSA_SECONDI)` tra le pagine (default 0.4 s) |
| Autenticazione Drive | OAuth2 con refresh token; credenziali lette da environment variable |
| Notifica email | SMTP diretto con `smtplib`; credenziali lette da environment variable |

---

*Architettura verificata al: 2026-06-11*
