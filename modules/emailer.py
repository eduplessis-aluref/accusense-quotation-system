import os
import smtplib
import ssl
import streamlit as st

from email.message import EmailMessage


def send_email(recipient, pdf_path, quote_number):

    try:
        sender_email = st.secrets["email"]["sender_email"]
        sender_password = st.secrets["email"]["sender_password"]
        smtp_server = st.secrets["email"].get("smtp_server", "smtp.gmail.com")
        smtp_port = int(st.secrets["email"].get("smtp_port", 465))

        subject = f"Quotation {quote_number}"

        body = f"""
Good day,

Please find attached quotation {quote_number}.

Kind regards,
AccuSense
"""

        msg = EmailMessage()
        msg["From"] = sender_email
        msg["To"] = recipient
        msg["Subject"] = subject
        msg.set_content(body)

        with open(pdf_path, "rb") as f:
            pdf_data = f.read()

        msg.add_attachment(
            pdf_data,
            maintype="application",
            subtype="pdf",
            filename=f"{quote_number}.pdf"
        )

        context = ssl.create_default_context()

        with smtplib.SMTP_SSL(
            smtp_server,
            smtp_port,
            context=context
        ) as server:
            server.login(
                sender_email,
                sender_password
            )

            server.send_message(msg)

        return True

    except Exception as e:
        st.error(f"Email error: {e}")
        return False