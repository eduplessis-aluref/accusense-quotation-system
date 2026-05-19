import os
import json
import datetime
import pandas as pd


QUOTE_FOLDER = "output/Quotes"
SPREADSHEET_NAME = "AccuSense Quote Database"


def ensure_quote_folder():
    os.makedirs(QUOTE_FOLDER, exist_ok=True)


def get_google_client():
    from modules.google_sheets import client
    return client


def generate_quote_number(salesperson):
    client = get_google_client()

    spreadsheet = client.open(SPREADSHEET_NAME)
    settings_sheet = spreadsheet.worksheet("Settings")

    current_number_raw = settings_sheet.acell("B1").value

    try:
        current_number = int(current_number_raw)
    except Exception:
        current_number = 1001

    next_number = current_number + 1
    settings_sheet.update("B1", [[next_number]])

    today = datetime.datetime.now()
    date_part = today.strftime("%Y%m%d")

    quote_number = f"Q-{date_part}-{current_number}"

    return quote_number


def calculate_totals(quote_df):
    if quote_df is None or quote_df.empty:
        return 0.0, 0.0, 0.0

    df = quote_df.copy()

    df["Qty"] = pd.to_numeric(df["Qty"], errors="coerce").fillna(0)
    df["Unit Price"] = pd.to_numeric(df["Unit Price"], errors="coerce").fillna(0)
    df["Discount"] = pd.to_numeric(df["Discount"], errors="coerce").fillna(0)

    df["Total"] = df["Qty"] * df["Unit Price"]

    subtotal = float(df["Total"].sum())
    vat = subtotal * 0.15
    grand_total = subtotal + vat

    return subtotal, vat, grand_total


def save_quote_json(
    quote_number,
    customer_name,
    company_name,
    site_name,
    customer_email,
    salesperson,
    salesperson_phone,
    salesperson_email,
    items,
    subtotal,
    vat,
    total,
    pdf_path
):
    ensure_quote_folder()

    saved_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    quote_data = {
        "quote_number": quote_number,
        "date_created": saved_at,
        "customer_name": customer_name,
        "company_name": company_name,
        "site_name": site_name,
        "customer_email": customer_email,
        "salesperson": salesperson,
        "salesperson_phone": salesperson_phone,
        "salesperson_email": salesperson_email,
        "items": items,
        "subtotal": subtotal,
        "vat": vat,
        "total": total,
        "pdf_path": pdf_path
    }

    file_path = os.path.join(QUOTE_FOLDER, f"{quote_number}.json")

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(quote_data, f, indent=4, ensure_ascii=False)

    save_quote_to_google_sheet(
        quote_number=quote_number,
        date_created=saved_at,
        salesperson=salesperson,
        customer_name=customer_name,
        company_name=company_name,
        site_name=site_name,
        subtotal=subtotal,
        vat=vat,
        total=total,
        pdf_path=pdf_path
    )

    return file_path


def save_quote_to_google_sheet(
    quote_number,
    date_created,
    salesperson,
    customer_name,
    company_name,
    site_name,
    subtotal,
    vat,
    total,
    pdf_path
):
    try:
        client = get_google_client()
        spreadsheet = client.open(SPREADSHEET_NAME)
        sheet = spreadsheet.worksheet("QuoteRegister")

        sheet.append_row([
            quote_number,
            date_created,
            salesperson,
            customer_name,
            company_name,
            site_name,
            round(float(subtotal), 2),
            round(float(vat), 2),
            round(float(total), 2),
            pdf_path
        ])

        return True

    except Exception as e:
        print(f"Google QuoteRegister save error: {e}")
        return False


def load_saved_quotes():
    ensure_quote_folder()

    files = [
        f for f in os.listdir(QUOTE_FOLDER)
        if f.endswith(".json")
    ]

    files.sort(reverse=True)
    return files


def load_quote_json(filename):
    ensure_quote_folder()

    file_path = os.path.join(QUOTE_FOLDER, filename)

    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def next_revision_number(base_quote_number):
    ensure_quote_folder()

    files = [
        f for f in os.listdir(QUOTE_FOLDER)
        if f.startswith(base_quote_number)
        and f.endswith(".json")
    ]

    return len(files) + 1