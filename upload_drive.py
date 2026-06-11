import os
import sys
from datetime import datetime, date
from pathlib import Path

from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/drive.file"]


def datesuffix(datada, dataa):
    MESI = ["gen", "feb", "mar", "apr", "mag", "giu", "lug", "ago", "set", "ott", "nov", "dic"]

    def _tok(d):
        try:
            dt = datetime.strptime(d, "%d/%m/%Y")
        except ValueError:
            raise ValueError(f"Formato data non valido: '{d}' — atteso DD/MM/YYYY")
        return f"{dt.day:02d}{MESI[dt.month - 1]}"

    if datada is None and dataa is None:
        return ""
    if datada is not None and dataa is None:
        return _tok(datada)
    if datada is None and dataa is not None:
        return _tok(dataa)
    return f"{_tok(datada)}_{_tok(dataa)}"


def nome_cartella(datada, dataa):
    suffix = datesuffix(datada, dataa)
    if suffix:
        return f"FESR_{suffix}"
    return f"FESR_{date.today().strftime('%Y%m%d')}"


def build_credentials(client_id, client_secret, refresh_token):
    creds = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        scopes=SCOPES,
    )
    try:
        creds.refresh(Request())
    except RefreshError:
        print("ERROR: impossibile rinnovare le credenziali Drive. Verificare GDRIVE_REFRESH_TOKEN.", file=sys.stderr)
        sys.exit(1)
    return creds


def create_subfolder(service, parent_id, name):
    body = {
        "name": name,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [parent_id],
    }
    result = service.files().create(body=body, fields="id").execute()
    subfolder_id = result.get("id")
    if not subfolder_id:
        raise RuntimeError(f"Drive API non ha restituito un ID per la sottocartella '{name}': {result}")
    print(f"Sottocartella creata: {name}")
    return subfolder_id


def upload_to_subfolder(folder_path, subfolder_id, service):
    uploaded = []
    for f in Path(folder_path).rglob("*"):
        if not f.is_file():
            continue
        media = MediaFileUpload(str(f), resumable=True)
        metadata = {"name": f.name, "parents": [subfolder_id]}
        try:
            result = service.files().create(
                body=metadata, media_body=media, fields="id,name"
            ).execute()
        except Exception as exc:
            print(f"ERROR: upload fallito per '{f.name}': {exc}", file=sys.stderr)
            raise
        uploaded.append(result)
        print(f"Caricato: {f.name}")
    return uploaded


def main():
    client_id = os.environ.get("GDRIVE_CLIENT_ID")
    client_secret = os.environ.get("GDRIVE_CLIENT_SECRET")
    refresh_token = os.environ.get("GDRIVE_REFRESH_TOKEN")
    folder_id = os.environ.get("GDRIVE_FOLDER_ID")
    output_folder = os.environ.get("FESR_OUTPUT", "data")

    for name, val in [
        ("GDRIVE_CLIENT_ID", client_id),
        ("GDRIVE_CLIENT_SECRET", client_secret),
        ("GDRIVE_REFRESH_TOKEN", refresh_token),
        ("GDRIVE_FOLDER_ID", folder_id),
    ]:
        if not val:
            print(f"ERROR: {name} non impostato", file=sys.stderr)
            sys.exit(1)

    if not Path(output_folder).is_dir():
        print(f"ERROR: cartella output '{output_folder}' non trovata — nessun file da caricare.", file=sys.stderr)
        sys.exit(1)

    creds = build_credentials(client_id, client_secret, refresh_token)
    service = build("drive", "v3", credentials=creds)
    datada = os.environ.get("FESR_DATA_DA")
    dataa = os.environ.get("FESR_DATA_A")
    cartella_nome = nome_cartella(datada, dataa)
    subfolder_id = create_subfolder(service, folder_id, cartella_nome)
    uploaded = upload_to_subfolder(output_folder, subfolder_id, service)
    subfolder_url = f"https://drive.google.com/drive/folders/{subfolder_id}"
    print(f"Caricati {len(uploaded)} file su Drive: {subfolder_url}")
    Path("drive_url.txt").write_text(subfolder_url, encoding="utf-8")


if __name__ == "__main__":
    main()
