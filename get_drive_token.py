"""
Esegui questo script UNA VOLTA in locale per ottenere il refresh token.
Poi salva il token come GitHub Secret GDRIVE_REFRESH_TOKEN.

Uso:
  python get_drive_token.py --client-id TUO_CLIENT_ID --client-secret TUO_CLIENT_SECRET
"""
import argparse
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/drive.file"]

parser = argparse.ArgumentParser()
parser.add_argument("--client-id", required=True)
parser.add_argument("--client-secret", required=True)
args = parser.parse_args()

flow = InstalledAppFlow.from_client_config(
    {
        "installed": {
            "client_id": args.client_id,
            "client_secret": args.client_secret,
            "redirect_uris": ["http://localhost"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    },
    SCOPES,
)

creds = flow.run_local_server(port=0)

print("\n" + "=" * 60)
print("GDRIVE_REFRESH_TOKEN (copialo come GitHub Secret):")
print(creds.refresh_token)
print("=" * 60 + "\n")
