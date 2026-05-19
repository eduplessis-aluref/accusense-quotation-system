import streamlit as st
import gspread
import pandas as pd

from google.oauth2.service_account import Credentials


# =====================================================
# GOOGLE SHEETS CONNECTION
# =====================================================

scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]


def get_credentials():

    try:
        service_account_info = dict(st.secrets["gcp_service_account"])

        creds = Credentials.from_service_account_info(
            service_account_info,
            scopes=scope
        )

        return creds

    except Exception:

        creds = Credentials.from_service_account_file(
            "credentials.json",
            scopes=scope
        )

        return creds


creds = get_credentials()
client = gspread.authorize(creds)


# =====================================================
# LOAD PRODUCTS
# =====================================================

def load_products():

    sheet = client.open(
        "AccuSense Quote Database"
    ).worksheet("Products")

    data = sheet.get_all_values()

    if not data:
        return pd.DataFrame()

    headers = [
        str(h).strip()
        for h in data[0]
    ]

    rows = data[1:]

    df = pd.DataFrame(
        rows,
        columns=headers
    )

    df = df.dropna(how="all")

    if "Selling Price" in df.columns:
        df["Selling Price"] = (
            df["Selling Price"]
            .astype(str)
            .str.replace(",", "", regex=False)
            .str.replace("R", "", regex=False)
            .str.strip()
        )

        df["Selling Price"] = pd.to_numeric(
            df["Selling Price"],
            errors="coerce"
        ).fillna(0)

    return df


# =====================================================
# LOAD TERMS
# =====================================================

def load_terms():

    try:
        sheet = client.open(
            "AccuSense Quote Database"
        ).worksheet("Terms")

        data = sheet.get_all_values()

        terms = ""

        for row in data[1:]:

            if len(row) > 0:

                text = str(row[0]).strip()

                if text != "":

                    terms += f"• {text}<br/>"

        return terms

    except Exception:

        return """
        • Prices exclude VAT<br/>
        • Valid for 30 days<br/>
        • Delivery subject to stock availability<br/>
        """


# =====================================================
# SAVE QUOTE TO GOOGLE SHEET
# =====================================================

def save_quote(
    quote_number,
    customer,
    company,
    salesperson,
    subtotal,
    vat,
    total,
    quote_df
):

    try:
        spreadsheet = client.open(
            "AccuSense Quote Database"
        )

        quotes_sheet = spreadsheet.worksheet(
            "QuoteRegister"
        )

        quotes_sheet.append_row([
            quote_number,
            customer,
            company,
            salesperson,
            subtotal,
            vat,
            total
        ])

        return True

    except Exception as e:
        print(f"Save quote error: {e}")
        return False