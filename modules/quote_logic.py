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


def get_spreadsheet():
    client = get_google_client()
    return client.open(SPREADSHEET_NAME)


def generate_quote_number(salesperson=""):
    spreadsheet = get_spreadsheet()
    settings_sheet = spreadsheet.worksheet("Settings")

    current_number_raw = settings_sheet.acell("B1").value

    try:
        current_number = int(current_number_raw)
    except Exception:
        current_number = 1001

    next_number = current_number + 1
    settings_sheet.update("B1", [[next_number]])

    date_part = datetime.datetime.now().strftime("%Y%m%d")

    return f"Q-{date_part}-{current_number}"


def get_base_quote_number(quote_number):
    quote_number = str(quote_number)

    if "-REV" in quote_number:
        return quote_number.split("-REV")[0]

    return quote_number


def next_revision_number(base_quote_number):
    spreadsheet = get_spreadsheet()
    register_sheet = spreadsheet.worksheet("QuoteRegister")

    rows = register_sheet.get_all_records()

    highest_revision = 0

    for row in rows:
        row_base = str(row.get("Base Quote Number", "")).strip()
        revision = str(row.get("Revision", "")).strip()

        if row_base == base_quote_number:
            if revision.upper().startswith("REV"):
                try:
                    rev_num = int(revision.upper().replace("REV", ""))
                    highest_revision = max(highest_revision, rev_num)
                except Exception:
                    pass

    return highest_revision + 1


def generate_revision_quote_number(base_quote_number):
    revision_number = next_revision_number(base_quote_number)
    return f"{base_quote_number}-REV{revision_number:02d}", f"REV{revision_number:02d}"


def calculate_totals(quote_df):
    if quote_df is None or quote_df.empty:
        return 0.0, 0.0, 0.0

    df = quote_df.copy()

    df["Qty"] = pd.to_numeric(df["Qty"], errors="coerce").fillna(0)
    df["Unit Price"] = pd.to_numeric(df["Unit Price"], errors="coerce").fillna(0)
    df["Discount"] = pd.to_numeric(df["Discount"], errors="coerce").fillna(0)

    df["Total"] = (
        df["Qty"]
        * df["Unit Price"]
        * (1 - df["Discount"] / 100)
    )

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

    date_created = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    base_quote_number = get_base_quote_number(quote_number)

    if "-REV" in quote_number:
        revision = quote_number.split("-")[-1]
    else:
        revision = "ORIGINAL"

    quote_data = {
        "quote_number": quote_number,
        "base_quote_number": base_quote_number,
        "revision": revision,
        "date_created": date_created,
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

    save_quote_to_google_sheets(quote_data)

    return file_path


def save_quote_to_google_sheets(quote_data):
    spreadsheet = get_spreadsheet()

    register_sheet = spreadsheet.worksheet("QuoteRegister")
    items_sheet = spreadsheet.worksheet("QuoteItems")

    register_sheet.append_row([
        quote_data["quote_number"],
        quote_data["base_quote_number"],
        quote_data["revision"],
        quote_data["date_created"],
        quote_data["salesperson"],
        quote_data["customer_name"],
        quote_data["company_name"],
        quote_data["site_name"],
        round(float(quote_data["subtotal"]), 2),
        round(float(quote_data["vat"]), 2),
        round(float(quote_data["total"]), 2),
        quote_data["pdf_path"]
    ])

    for idx, item in enumerate(quote_data["items"], start=1):
        items_sheet.append_row([
            quote_data["quote_number"],
            idx,
            item.get("Identification", ""),
            item.get("Product", ""),
            item.get("Description", ""),
            item.get("Billing", ""),
            item.get("Qty", 0),
            item.get("Discount", 0),
            item.get("Unit Price", 0),
            item.get("Total", 0)
        ])


def load_saved_quotes():
    spreadsheet = get_spreadsheet()
    register_sheet = spreadsheet.worksheet("QuoteRegister")

    rows = register_sheet.get_all_records()

    quote_numbers = []

    for row in rows:
        quote_number = str(row.get("Quote Number", "")).strip()
        if quote_number:
            quote_numbers.append(quote_number)

    quote_numbers = sorted(list(set(quote_numbers)), reverse=True)

    return quote_numbers


def load_quote_json(quote_number):
    spreadsheet = get_spreadsheet()

    register_sheet = spreadsheet.worksheet("QuoteRegister")
    items_sheet = spreadsheet.worksheet("QuoteItems")

    register_rows = register_sheet.get_all_records()
    item_rows = items_sheet.get_all_records()

    selected_register = None

    for row in register_rows:
        if str(row.get("Quote Number", "")).strip() == str(quote_number).strip():
            selected_register = row
            break

    if selected_register is None:
        raise ValueError(f"Quote not found: {quote_number}")

    items = []

    for row in item_rows:
        if str(row.get("Quote Number", "")).strip() == str(quote_number).strip():
            items.append({
                "Identification": row.get("Identification", ""),
                "Product": row.get("Product", ""),
                "Description": row.get("Description", ""),
                "Billing": row.get("Billing", ""),
                "Qty": row.get("Qty", 1),
                "Discount": row.get("Discount", 0),
                "Unit Price": row.get("Unit Price", 0),
                "Total": row.get("Total", 0)
            })

    return {
        "quote_number": selected_register.get("Quote Number", ""),
        "base_quote_number": selected_register.get("Base Quote Number", ""),
        "revision": selected_register.get("Revision", ""),
        "date_created": selected_register.get("Date Created", ""),
        "customer_name": selected_register.get("Customer", ""),
        "company_name": selected_register.get("Company", ""),
        "site_name": selected_register.get("Site", ""),
        "salesperson": selected_register.get("Salesperson", ""),
        "salesperson_phone": "",
        "salesperson_email": "",
        "items": items,
        "subtotal": selected_register.get("Subtotal", 0),
        "vat": selected_register.get("VAT", 0),
        "total": selected_register.get("Total", 0),
        "pdf_path": selected_register.get("PDF Path", "")
    }