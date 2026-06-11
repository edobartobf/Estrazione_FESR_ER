import os
import sys
from datetime import datetime, date
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/drive.file"]


def datesuffix(datada, dataa):
    MESI = ["gen", "feb", "mar", "apr", "mag", "giu", "lug", "ago", "set", "ott", "nov", "dic"]

    def _tok(d):
        dt = datetime.strptime(d, "%d/%m/%Y")
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
    creds.refresh(Request())
    return creds


def upload_folder(folder_path, folder_id, creds):
    service = build("drive", "v3", credentials=creds)
    uploaded = []
    for f in Path(folder_path).rglob("*"):
        if not f.is_file():
            continue
        media = MediaFileUpload(str(f), resumable=True)
        metadata = {"name": f.name, "parents": [folder_id]}
        result = service.files().create(
            body=metadata, media_body=media, fields="id,name"
        ).execute()
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

    creds = build_credentials(client_id, client_secret, refresh_token)
    uploaded = upload_folder(output_folder, folder_id, creds)
    folder_url = f"https://drive.google.com/drive/folders/{folder_id}"
    print(f"Caricati {len(uploaded)} file su Drive: {folder_url}")
    Path("drive_url.txt").write_text(folder_url, encoding="utf-8")


if __name__ == "__main__":
    main()
