import json
import os
import sys
from pathlib import Path

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/drive.file"]


def upload_folder(folder_path, folder_id, sa_json_str):
    creds = service_account.Credentials.from_service_account_info(
        json.loads(sa_json_str), scopes=SCOPES
    )
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
    sa_json = os.environ.get("GDRIVE_SA_JSON")
    folder_id = os.environ.get("GDRIVE_FOLDER_ID")
    output_folder = os.environ.get("FESR_OUTPUT", "data")

    if not sa_json:
        print("ERROR: GDRIVE_SA_JSON non impostato", file=sys.stderr)
        sys.exit(1)
    if not folder_id:
        print("ERROR: GDRIVE_FOLDER_ID non impostato", file=sys.stderr)
        sys.exit(1)

    uploaded = upload_folder(output_folder, folder_id, sa_json)
    folder_url = f"https://drive.google.com/drive/folders/{folder_id}"
    print(f"Caricati {len(uploaded)} file su Drive: {folder_url}")
    Path("drive_url.txt").write_text(folder_url, encoding="utf-8")


if __name__ == "__main__":
    main()
