import smtplib
from email.message import EmailMessage
import os

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

EMAIL_USER = "YOUR_EMAIL@gmail.com"
EMAIL_PASSWORD = "YOUR_APP_PASSWORD"


def send_email(recipient, pdf_path, quote_number):

    try:
        if EMAIL_USER == "YOUR_EMAIL@gmail.com":
            print("Email settings not configured.")
            return False

        msg = EmailMessage()

        msg["Subject"] = f"Quotation {quote_number}"
        msg["From"] = EMAIL_USER
        msg["To"] = recipient

        msg.set_content(
            f"""Dear Customer,

Please find attached quotation {quote_number}.

Kind regards,
AccuSense
"""
        )

        with open(pdf_path, "rb") as f:
            file_data = f.read()
            file_name = os.path.basename(pdf_path)

        msg.add_attachment(
            file_data,
            maintype="application",
            subtype="pdf",
            filename=file_name
        )

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
            smtp.starttls()
            smtp.login(EMAIL_USER, EMAIL_PASSWORD)
            smtp.send_message(msg)

        return True

    except Exception as e:
        print(f"Email error: {e}")
        return False