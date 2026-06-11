import csv
import os
import smtplib
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path


def build_summary(output_folder):
    records = []
    for csv_path in Path(output_folder).glob("delibere_*.csv"):
        try:
            with csv_path.open(encoding="utf-8", newline="") as fh:
                records.extend(list(csv.DictReader(fh)))
        except Exception:
            pass
    azioni = sorted({
        a.strip()
        for r in records
        for a in r.get("azioni", "").split(";")
        if a.strip()
    })
    return {"count": len(records), "azioni": azioni}


def send_email(smtp_host, smtp_port, smtp_user, smtp_pass, recipients, subject, body):
    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["From"] = smtp_user
    msg["To"] = ", ".join(recipients)
    msg.attach(MIMEText(body, "plain", "utf-8"))
    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.sendmail(smtp_user, recipients, msg.as_string())


def main():
    smtp_host = os.environ.get("SMTP_HOST")
    smtp_user = os.environ.get("SMTP_USER")
    smtp_pass = os.environ.get("SMTP_PASS")
    recipients_raw = os.environ.get("EMAIL_RECIPIENTS")

    for name, val in [
        ("SMTP_HOST", smtp_host),
        ("SMTP_USER", smtp_user),
        ("SMTP_PASS", smtp_pass),
        ("EMAIL_RECIPIENTS", recipients_raw),
    ]:
        if not val:
            print(f"ERROR: {name} non impostato", file=sys.stderr)
            sys.exit(1)

    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    output_folder = os.environ.get("FESR_OUTPUT", "data")
    drive_url_path = Path("drive_url.txt")
    drive_url = drive_url_path.read_text(encoding="utf-8").strip() if drive_url_path.exists() else "N/D"

    summary = build_summary(output_folder)
    recipients = [r.strip() for r in recipients_raw.split(",") if r.strip()]
    azioni_str = ", ".join(summary["azioni"]) if summary["azioni"] else "nessuna"

    subject = f"FESR Scraper — {summary['count']} delibere trovate"
    body = (
        f"Riepilogo FESR — run automatico\n\n"
        f"Delibere trovate: {summary['count']}\n"
        f"Azioni identificate: {azioni_str}\n"
        f"Cartella Drive: {drive_url}\n"
    )

    send_email(smtp_host, smtp_port, smtp_user, smtp_pass, recipients, subject, body)
    print(f"Email inviata a {len(recipients)} destinatari.")


if __name__ == "__main__":
    main()
