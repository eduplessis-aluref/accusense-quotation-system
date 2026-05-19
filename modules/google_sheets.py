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

creds = Credentials.from_service_account_file(
    "credentials.json",
    scopes=scope
)

client = gspread.authorize(creds)

# =====================================================
# LOAD PRODUCTS
# =====================================================

def load_products():

    sheet = client.open(
        "Quotation Database"
    ).worksheet("Products")

    data = sheet.get_all_values()

    # =================================================
    # HEADERS
    # =================================================

    raw_headers = data[0]

    headers = []

    for i, h in enumerate(raw_headers):

        h = str(h).strip()

        if h == "":

            h = f"Column_{i}"

        if h in headers:

            h = f"{h}_{i}"

        headers.append(h)

    rows = data[1:]

    df = pd.DataFrame(
        rows,
        columns=headers
    )

    # =================================================
    # FIND DESCRIPTION COLUMN
    # =================================================

    description_column = None

    possible_description_columns = [

        "Description",
        "description",
        "Item Description",
        "Product Description",
        "Details"
    ]

    for col in possible_description_columns:

        if col in df.columns:

            description_column = col

            break

    if description_column is None:

        description_column = df.columns[0]

    df["Description"] = df[
        description_column
    ]

    # =================================================
    # FIND SHORT NAME
    # =================================================

    if "Short Name" not in df.columns:

        df["Short Name"] = df["Description"]

    # =================================================
    # FIND SELLING PRICE
    # =================================================

    price_column = None

    possible_price_columns = [

        "Selling Price",
        "Selling price",
        "Price",
        "Selling",
        "Sell Price"
    ]

    for col in possible_price_columns:

        if col in df.columns:

            price_column = col

            break

    if price_column is None:

        df["Selling Price"] = 0

    else:

        df["Selling Price"] = (

            df[price_column]

            .astype(str)

            .str.replace(",", "")

            .str.replace("R", "")

            .str.strip()
        )

        df["Selling Price"] = pd.to_numeric(

            df["Selling Price"],

            errors="coerce"

        ).fillna(0)

    # =================================================
    # BILLING COLUMN
    # =================================================

    if "Billing" not in df.columns:

        df["Billing"] = "Once-Off"

    # =================================================
    # REMOVE EMPTY ROWS
    # =================================================

    df = df[
        df["Description"]
        .astype(str)
        .str.strip() != ""
    ]

    return df

# =====================================================
# LOAD TERMS
# =====================================================

def load_terms():

    try:

        sheet = client.open(
            "Quotation Database"
        ).worksheet("Terms")

        data = sheet.get_all_values()

        terms = ""

        for row in data[1:]:

            if len(row) > 0:

                text = str(row[0]).strip()

                if text != "":

                    terms += f"• {text}<br/>"

        return terms

    except:

        return """
        • Prices exclude VAT unless stated otherwise.<br/>
        • Quotation valid for 30 days.<br/>
        • Delivery subject to stock availability.<br/>
        """

# =====================================================
# SAVE QUOTE
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
            "Quotation Database"
        )

        quotes_sheet = spreadsheet.worksheet(
            "Quotes"
        )

        items_sheet = spreadsheet.worksheet(
            "QuoteItems"
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

        for _, row in quote_df.iterrows():

            items_sheet.append_row([

                quote_number,

                row["Product"],

                row["Qty"],

                row["Discount"],

                row["Unit Price"],

                row["Total"]
            ])

    except Exception as e:

        print(f"Save error: {e}")