import csv
import json
import re
import time
from collections import Counter
from datetime import datetime
from pathlib import Path
from urllib.parse import unquote, urljoin

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://servizissiir.regione.emilia-romagna.it/deliberegiunta/servlet/AdapterHTTP"
BASE_DIR = "https://servizissiir.regione.emilia-romagna.it/deliberegiunta/servlet/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/125.0 Safari/537.36"
}

FIELDNAMES = [
    "anno_ricerca",
    "keyword_ricerca",
    "pagina",
    "proponente",
    "tipo_atto",
    "numero_adozione",
    "data_adozione",
    "protocollo",
    "oggetto",
    "pubblicazione_bur",
    "data_pubblicazione_bur",
    "dettaglio_url",
    "pdf_url",
    "programma",
    "azioni",
    "priorita",
    "cup",
    "dgr",
    "determinazioni",
    "tipo_manovra",
    "beneficiario",
    "importi",
]


def decodehtml(response):
    return response.content.decode("ISO-8859-1", errors="replace")


def buildpayload(anno, keyword, datada=None, dataa=None, tipoatto=""):
    return {
        "REFRESH": "Y",
        "actionURL": "AdapterHTTP?ACTION_NAME=ACTIONRICERCADELIBERE",
        "ENTE": "1",
        "tipoAtto": tipoatto,
        "annoAdozione": str(anno),
        "numAdozione": "",
        "dataAdozioneDa": datada or "",
        "dataAdozioneA": dataa or "",
        "oggetto": keyword,
        "did": "true",
        "QUERY_STRING{ACTION_NAME=ACTIONRICERCADELIBERE&POPULATING=LIST&tableId=ricerca_delibere&HTML_POINTER=submitRicerca}": "Cerca",
        "PAG_SIZE_ricerca_delibere": "10",
    }


def buildpageparams(anno, keyword, page, datada=None, dataa=None, tipoatto=""):
    return {
        "ANNOADOZIONE": str(anno),
        "REFRESH": "Y",
        "ACTIONURL": "AdapterHTTP?ACTION_NAME=ACTIONRICERCADELIBERE",
        "OGGETTO": keyword,
        "ACTION_NAME": "ACTIONRICERCADELIBERE",
        "POPULATING": "LIST",
        "TABLEID": "ricerca_delibere",
        "HTML_POINTER": "submitRicerca",
        "PAG_SIZE_RICERCA_DELIBERE": "10",
        "TIPOATTO": tipoatto,
        "DATAADOZIONEA": dataa or "",
        "DATAADOZIONEDA": datada or "",
        "NUMADOZIONE": "",
        "ENTE": "1",
        "DID": "true",
        "ricerca_delibere_LIST_PAGE": str(page),
    }


def fetchfirstpage(session, anno, keyword, timeout, datada=None, dataa=None, tipoatto=""):
    response = session.post(BASE_URL, data=buildpayload(anno, keyword, datada=datada, dataa=dataa, tipoatto=tipoatto), timeout=timeout)
    response.raise_for_status()
    return decodehtml(response)


def fetchpage(session, anno, keyword, page, timeout, datada=None, dataa=None, tipoatto=""):
    if page == 1:
        return fetchfirstpage(session, anno, keyword, timeout, datada=datada, dataa=dataa, tipoatto=tipoatto)
    response = session.get(BASE_URL, params=buildpageparams(anno, keyword, page, datada=datada, dataa=dataa, tipoatto=tipoatto), timeout=timeout)
    response.raise_for_status()
    return decodehtml(response)


def parsecounter(soup):
    table = soup.find("table", class_="contatore")
    if not table:
        return {"current_page": 1, "total_pages": 1, "total_records": 0}
    text = cleantext(table.get_text(" ", strip=True))
    match = re.search(r"Pag\.\s*(\d+)\s+di\s+(\d+).*?di\s+(\d+)\)", text, re.I)
    if not match:
        return {"current_page": 1, "total_pages": 1, "total_records": 0, "counter_text": text}
    return {
        "current_page": int(match.group(1)),
        "total_pages": int(match.group(2)),
        "total_records": int(match.group(3)),
        "counter_text": text,
    }


def cleantext(value):
    return re.sub(r"\s+", " ", value or "").strip()


def parseoggetto(cell):
    link = cell.find("a", class_="linkatto")
    protocollo = cleantext(link.get_text(" ", strip=True)) if link else ""
    dettaglio = urljoin(BASE_URL, link.get("href")) if link and link.get("href") else ""
    parts = [cleantext(part) for part in cell.stripped_strings]
    parts = [part for part in parts if part]
    if parts and parts[0] == protocollo:
        parts = parts[1:]
    oggetto = cleantext(" ".join(parts))
    return protocollo, oggetto, dettaglio


def findall(pattern, text):
    values = re.findall(pattern, text or "", flags=re.I)
    cleaned = []
    for value in values:
        if isinstance(value, tuple):
            value = next((item for item in value if item), "")
        value = cleantext(str(value)).upper()
        if value and value not in cleaned:
            cleaned.append(value)
    return cleaned


def classifymanovra(text):
    upper = (text or "").upper()
    checks = [
        ("revoca", ["REVOCA"]),
        ("liquidazione saldo", ["LIQUIDAZIONE SALDO", "SALDO IN UNICA SOLUZIONE"]),
        ("liquidazione sal", ["LIQUIDAZIONE SAL"]),
        ("liquidazione", ["LIQUIDAZIONE"]),
        ("concessione", ["CONCESSIONE", "CONCESSO"]),
        ("approvazione", ["APPROVAZIONE", "APPROVATO"]),
        ("impegno", ["IMPEGNO", "IMPEGNARE"]),
        ("accertamento", ["ACCERTAMENTO"]),
        ("proroga", ["PROROGA"]),
        ("rideterminazione", ["RIDETERMINAZIONE"]),
        ("modifica", ["MODIFICA", "VARIAZIONE"]),
        ("scorrimento", ["SCORRIMENTO"]),
        ("ammissione", ["AMMISSIONE", "AMMESS"]),
    ]
    for label, keywords in checks:
        if any(keyword in upper for keyword in keywords):
            return label
    return "altro"


def extractbeneficiario(text):
    patterns = [
        r"A FAVORE (?:DEL|DELLA|DELL'|DEI|DEGLI|DELLE|DI)\s+(.+?)(?:\s+PER\s+LA|\s+PER\s+IL|\s+CUP\b|\s+-\s+|\.$)",
        r"BENEFICIARI(?:O|A)?\s+(.+?)(?:\s+PER\s+LA|\s+PER\s+IL|\s+CUP\b|\s+-\s+|\.$)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text or "", flags=re.I)
        if match:
            return cleantext(match.group(1).strip(" .;:-\"'"))
    return ""


def enrichrecord(record):
    text = record.get("oggetto", "")
    upper = text.upper()
    record["programma"] = "PR FESR 2021-2027" if "FESR" in upper else ""
    record["azioni"] = ";".join(findall(r"\b\d\.\d\.\d\b", text))
    record["priorita"] = ";".join(findall(r"PRIORITA'?[\s.:-]*(\d+)", text))
    record["cup"] = ";".join(findall(r"\b[A-Z][0-9]{2}[A-Z0-9]{12}\b", text))
    record["dgr"] = ";".join(findall(r"D\.?\s*G\.?\s*R\.?\s*(?:N\.?\s*)?(\d+/\d{4})", text))
    record["determinazioni"] = ";".join(findall(r"DET(?:ERMINAZION(?:E|I))?\.?\s*(?:N\.?\s*)?(\d+(?:/\d{4})?)", text))
    record["tipo_manovra"] = classifymanovra(text)
    record["beneficiario"] = extractbeneficiario(text)
    record["importi"] = ";".join(findall(r"(?:EURO|EUR|€)\s*([0-9][0-9.\s]*,\d{2})", text))
    return record


def parserows(html, anno, keyword, page):
    soup = BeautifulSoup(html, "html.parser")
    records = []
    for row in soup.select("tr[id^='ricerca_delibere_tr_']"):
        cells = row.find_all("td")
        if len(cells) < 7:
            continue
        protocollo, oggetto, dettaglio = parseoggetto(cells[4])
        if not any([protocollo, oggetto, cleantext(cells[0].get_text(" ", strip=True))]):
            continue
        record = {
            "anno_ricerca": str(anno),
            "keyword_ricerca": keyword,
            "pagina": str(page),
            "proponente": cleantext(cells[0].get_text(" ", strip=True)),
            "tipo_atto": cleantext(cells[1].get_text(" ", strip=True)),
            "numero_adozione": cleantext(cells[2].get_text(" ", strip=True)),
            "data_adozione": cleantext(cells[3].get_text(" ", strip=True)),
            "protocollo": protocollo,
            "oggetto": oggetto,
            "pubblicazione_bur": cleantext(cells[5].get_text(" ", strip=True)),
            "data_pubblicazione_bur": cleantext(cells[6].get_text(" ", strip=True)),
            "dettaglio_url": dettaglio,
            "pdf_url": "",
        }
        records.append(enrichrecord(record))
    return records, parsecounter(soup)


def findpdflink(session, dettaglio, timeout):
    if not dettaglio:
        return ""
    response = session.get(dettaglio, timeout=timeout)
    response.raise_for_status()
    soup = BeautifulSoup(decodehtml(response), "html.parser")
    link = soup.find("a", attrs={"target": "_blank"}, class_="linkatto")
    if not link or not link.get("href"):
        link = soup.find("a", href=re.compile("downloadTesto", re.I))
    return urljoin(BASE_URL, link.get("href")) if link and link.get("href") else ""


def contentfilename(response, fallback):
    header = response.headers.get("Content-Disposition", "")
    match = re.search(r'filename="([^"]+)"', header)
    if match:
        return Path(unquote(match.group(1))).name
    return fallback


def downloadpdf(session, url, folder, fallback, timeout):
    folder.mkdir(parents=True, exist_ok=True)
    response = session.get(url, stream=True, timeout=timeout)
    response.raise_for_status()
    filename = contentfilename(response, fallback)
    path = folder / filename
    with path.open("wb") as handle:
        for chunk in response.iter_content(chunk_size=65536):
            if chunk:
                handle.write(chunk)
    return str(path)


def scraperesults(
    anno,
    keyword,
    maxpages=None,
    delay=0.4,
    includelinks=False,
    download=False,
    maxpdf=None,
    timeout=30,
    outputfolder="data",
    datada=None,
    dataa=None,
    tipoatto="",
):
    for label, value in (("datada", datada), ("dataa", dataa)):
        if value is not None:
            try:
                datetime.strptime(value, "%d/%m/%Y")
            except ValueError:
                raise ValueError(f"{label} deve essere nel formato DD/MM/YYYY, ricevuto: {value!r}")
    session = requests.Session()
    session.headers.update(HEADERS)
    allrecords = []
    totalpages = None
    page = 1
    pdfcount = 0
    while True:
        html = fetchpage(session, anno, keyword, page, timeout, datada=datada, dataa=dataa, tipoatto=tipoatto)
        records, counter = parserows(html, anno, keyword, page)
        if totalpages is None:
            totalpages = counter.get("total_pages") or 1
            totalrecords = counter.get("total_records") or len(records)
            print(f"Trovati {totalrecords} risultati in {totalpages} pagine.")
        for record in records:
            if includelinks or download:
                record["pdf_url"] = findpdflink(session, record["dettaglio_url"], timeout)
                time.sleep(delay)
            if download and record["pdf_url"] and (maxpdf is None or pdfcount < maxpdf):
                fallback = f"{record['protocollo'].replace('/', '-')}.pdf"
                record["pdf_file"] = downloadpdf(
                    session,
                    record["pdf_url"],
                    Path(outputfolder) / "pdf",
                    fallback,
                    timeout,
                )
                pdfcount += 1
                time.sleep(delay)
        allrecords.extend(records)
        print(f"Pagina {page}/{totalpages}: {len(records)} righe, totale {len(allrecords)}.")
        if page >= totalpages:
            break
        if maxpages is not None and page >= maxpages:
            break
        page += 1
        time.sleep(delay)
    return allrecords


def writecsv(path, records, fieldnames=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    names = fieldnames or FIELDNAMES
    extras = sorted({key for record in records for key in record.keys()} - set(names))
    names = names + extras
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=names)
        writer.writeheader()
        writer.writerows(records)


def writejson(path, records):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")


def splitvalues(value):
    return [part.strip() for part in (value or "").split(";") if part.strip()]


def countfield(records, field):
    counter = Counter()
    for record in records:
        values = splitvalues(record.get(field, ""))
        if not values:
            values = ["non rilevato"]
        for value in values:
            counter[value] += 1
    return [{"valore": value, "conteggio": count} for value, count in counter.most_common()]


def writesummary(path, rows):
    writecsv(path, rows, ["valore", "conteggio"])


def writesummaries(records, anno, keyword, folder, date_suffix=None):
    suffix = date_suffix if date_suffix else f"{anno}_{keyword.lower()}".replace(" ", "_")
    writesummary(folder / f"riepilogo_azioni_{suffix}.csv", countfield(records, "azioni"))
    writesummary(folder / f"riepilogo_manovre_{suffix}.csv", countfield(records, "tipo_manovra"))
    writesummary(folder / f"riepilogo_beneficiari_{suffix}.csv", countfield(records, "beneficiario"))
    writesummary(folder / f"riepilogo_proponenti_{suffix}.csv", countfield(records, "proponente"))
