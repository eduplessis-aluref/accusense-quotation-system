import os
import json
from datetime import datetime

QUOTE_FOLDER = "output/Quotes"

def salesperson_initials(salesperson):
    if not salesperson.strip():
        return "XX"

    parts = salesperson.strip().split()

    if len(parts) >= 2:
        return (parts[0][0] + parts[-1][0]).upper()

    return parts[0][0].upper() + "X"


def generate_quote_number(salesperson):
    os.makedirs(QUOTE_FOLDER, exist_ok=True)

    initials = salesperson_initials(salesperson)
    today = datetime.now().strftime("%Y%m%d")

    existing = [
        f for f in os.listdir(QUOTE_FOLDER)
        if f.startswith(f"{initials}-{today}") and f.endswith(".json")
    ]

    base_numbers = []

    for file in existing:
        clean = file.replace(".json", "")
        clean = clean.split("-REV")[0]

        try:
            number = int(clean.split("-")[-1])
            base_numbers.append(number)
        except:
            pass

    next_number = max(base_numbers) + 1 if base_numbers else 1

    return f"{initials}-{today}-{next_number:02d}"


def next_revision_number(base_quote_number):
    os.makedirs(QUOTE_FOLDER, exist_ok=True)

    base = base_quote_number.split("-REV")[0]

    revisions = []

    for file in os.listdir(QUOTE_FOLDER):
        if file.startswith(base) and "-REV" in file:
            try:
                rev = int(file.replace(".json", "").split("-REV")[-1])
                revisions.append(rev)
            except:
                pass

    return max(revisions) + 1 if revisions else 1


def calculate_totals(df):
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
    os.makedirs(QUOTE_FOLDER, exist_ok=True)

    data = {
        "quote_number": quote_number,
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
        "pdf_path": pdf_path,
        "saved_at": datetime.now().isoformat()
    }

    file_path = os.path.join(QUOTE_FOLDER, f"{quote_number}.json")

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def load_saved_quotes():
    os.makedirs(QUOTE_FOLDER, exist_ok=True)

    quotes = [
        f.replace(".json", "")
        for f in os.listdir(QUOTE_FOLDER)
        if f.endswith(".json")
    ]

    return sorted(quotes, reverse=True)


def load_quote_json(quote_number):
    file_path = os.path.join(QUOTE_FOLDER, f"{quote_number}.json")

    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)