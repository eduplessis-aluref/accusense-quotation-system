import os
import json
import streamlit as st
import gspread
import pandas as pd

from google.oauth2.service_account import Credentials


SPREADSHEET_NAME = "AccuSense Quote Database"

scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]


def get_credentials():

    if "gcp_service_account_json" in st.secrets:

        service_account_info = json.loads(
            st.secrets["gcp_service_account_json"]
        )

        creds = Credentials.from_service_account_info(
            service_account_info,
            scopes=scope
        )

        return creds

    if "gcp_service_account" in st.secrets:

        service_account_info = dict(
            st.secrets["gcp_service_account"]
        )

        creds = Credentials.from_service_account_info(
            service_account_info,
            scopes=scope
        )

        return creds

    if os.path.exists("credentials.json"):

        creds = Credentials.from_service_account_file(
            "credentials.json",
            scopes=scope
        )

        return creds

    st.error(
        "Google credentials not found. Add credentials in Streamlit Cloud secrets."
    )

    st.stop()


creds = get_credentials()
client = gspread.authorize(creds)


def load_products():

    sheet = client.open(
        SPREADSHEET_NAME
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


def load_terms():

    try:

        sheet = client.open(
            SPREADSHEET_NAME
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


def load_solution_templates():

    try:

        sheet = client.open(
            SPREADSHEET_NAME
        ).worksheet("SolutionTemplates")

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

        required_columns = [
            "Template Name",
            "Line No",
            "Identification",
            "Short Name",
            "Qty",
            "Discount",
            "Locked"
        ]

        for col in required_columns:

            if col not in df.columns:
                df[col] = ""

        df["Template Name"] = (
            df["Template Name"]
            .astype(str)
            .str.strip()
        )

        df["Identification"] = (
            df["Identification"]
            .astype(str)
            .str.strip()
        )

        df["Short Name"] = (
            df["Short Name"]
            .astype(str)
            .str.strip()
        )

        df["Qty"] = pd.to_numeric(
            df["Qty"],
            errors="coerce"
        ).fillna(1)

        df["Discount"] = pd.to_numeric(
            df["Discount"],
            errors="coerce"
        ).fillna(0)

        df["Line No"] = pd.to_numeric(
            df["Line No"],
            errors="coerce"
        ).fillna(0)

        df = df.sort_values(
            by=[
                "Template Name",
                "Line No"
            ]
        )

        return df

    except Exception as e:

        print(f"Template load error: {e}")

        return pd.DataFrame()


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
            SPREADSHEET_NAME
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

def load_users():

    try:

        sheet = client.open(
            SPREADSHEET_NAME
        ).worksheet("Users")

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

        df.columns = (
            df.columns
            .astype(str)
            .str.strip()
        )

        return df

    except Exception as e:

        st.error(f"User load error: {e}")

        return pd.DataFrame()        