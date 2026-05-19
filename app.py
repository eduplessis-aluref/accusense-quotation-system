import os
import streamlit as st
import pandas as pd

from modules.google_sheets import load_products, load_terms
from modules.quote_logic import (
    generate_quote_number,
    calculate_totals,
    save_quote_json,
    load_saved_quotes,
    load_quote_json,
    next_revision_number,
)
from modules.pdf_generator import generate_pdf
from modules.emailer import send_email

st.set_page_config(page_title="AccuSense Quotation System", layout="wide")
st.title("📄 AccuSense Quotation System")

os.makedirs("output/PDFs", exist_ok=True)
os.makedirs("output/Quotes", exist_ok=True)

@st.cache_data(ttl=300)
def get_cached_products():
    return load_products()

@st.cache_data(ttl=300)
def get_cached_terms():
    return load_terms()

if st.sidebar.button("Refresh Google Sheet Data"):
    st.cache_data.clear()
    st.rerun()

try:
    products_df = get_cached_products()
    terms = get_cached_terms()
except Exception as e:
    import traceback

st.error(str(e))
st.code(traceback.format_exc())
    st.stop()

if products_df.empty:
    st.error("No products found in Google Sheet.")
    st.stop()

required_columns = [
    "Identification",
    "Short Name",
    "Description",
    "Selling Price",
    "Billing"
]

missing_columns = [
    col for col in required_columns
    if col not in products_df.columns
]

if missing_columns:
    st.error(f"Missing columns in Products sheet: {missing_columns}")
    st.write("Current columns found:")
    st.write(list(products_df.columns))
    st.stop()

products_df["Identification"] = products_df["Identification"].fillna("General").astype(str).str.strip()
products_df["Identification"] = products_df["Identification"].replace("", "General")
products_df["Short Name"] = products_df["Short Name"].astype(str).str.strip()
products_df["Description"] = products_df["Description"].astype(str).str.strip()
products_df["Billing"] = products_df["Billing"].astype(str).str.strip()

products_df["Selling Price"] = (
    products_df["Selling Price"]
    .astype(str)
    .str.replace(",", "", regex=False)
    .str.replace("R", "", regex=False)
    .str.strip()
)

products_df["Selling Price"] = pd.to_numeric(
    products_df["Selling Price"],
    errors="coerce"
).fillna(0)

if "quote_items" not in st.session_state:
    st.session_state.quote_items = []

if "loaded_quote_number" not in st.session_state:
    st.session_state.loaded_quote_number = ""

# -------------------------------------------------
# LOAD / REVISE EXISTING QUOTE
# -------------------------------------------------

st.sidebar.header("Quote Options")

saved_quotes = load_saved_quotes()

if saved_quotes:
    selected_saved_quote = st.sidebar.selectbox(
        "Load Previous Quote",
        [""] + saved_quotes
    )

    if st.sidebar.button("Load Quote") and selected_saved_quote:
        quote_data = load_quote_json(selected_saved_quote)

        st.session_state.quote_items = quote_data.get("items", [])
        st.session_state.loaded_quote_number = quote_data.get("quote_number", "")

        st.session_state.customer_name = quote_data.get("customer_name", "")
        st.session_state.company_name = quote_data.get("company_name", "")
        st.session_state.site_name = quote_data.get("site_name", "")
        st.session_state.customer_email = quote_data.get("customer_email", "")
        st.session_state.salesperson = quote_data.get("salesperson", "")
        st.session_state.salesperson_phone = quote_data.get("salesperson_phone", "")
        st.session_state.salesperson_email = quote_data.get("salesperson_email", "")

        st.success("Quote loaded")

# -------------------------------------------------
# CUSTOMER DETAILS
# -------------------------------------------------

st.sidebar.header("Customer Details")

customer_name = st.sidebar.text_input(
    "Customer Name",
    value=st.session_state.get("customer_name", "")
)

company_name = st.sidebar.text_input(
    "Company",
    value=st.session_state.get("company_name", "")
)

site_name = st.sidebar.text_input(
    "Site",
    value=st.session_state.get("site_name", "")
)

customer_email = st.sidebar.text_input(
    "Customer Email",
    value=st.session_state.get("customer_email", "")
)

# -------------------------------------------------
# SALESPERSON DETAILS
# -------------------------------------------------

st.sidebar.header("Salesperson Details")

salesperson = st.sidebar.text_input(
    "Salesperson Name",
    value=st.session_state.get("salesperson", "Eddie du Plessis")
)

salesperson_phone = st.sidebar.text_input(
    "Salesperson Phone",
    value=st.session_state.get("salesperson_phone", "")
)

salesperson_email = st.sidebar.text_input(
    "Salesperson Email",
    value=st.session_state.get("salesperson_email", "")
)

# -------------------------------------------------
# QUOTE NUMBER
# -------------------------------------------------

if st.session_state.loaded_quote_number:
    revision = next_revision_number(st.session_state.loaded_quote_number)
    quote_number = f"{st.session_state.loaded_quote_number}-REV{revision}"
else:
    quote_number = generate_quote_number(salesperson)

st.sidebar.write("### Quote Number")
st.sidebar.write(quote_number)

# -------------------------------------------------
# PRODUCT SELECTION
# -------------------------------------------------

st.header("Add Products")

category_list = sorted(
    products_df["Identification"]
    .dropna()
    .astype(str)
    .unique()
)

selected_identification = st.selectbox(
    "Select Main Category",
    category_list
)

category_df = products_df[
    products_df["Identification"] == selected_identification
].copy()

product_list = sorted(
    category_df["Short Name"]
    .dropna()
    .astype(str)
    .unique()
)

selected_short_name = st.selectbox(
    "Select Product",
    product_list
)

selected_rows = category_df[
    category_df["Short Name"] == selected_short_name
]

if selected_rows.empty:
    st.warning("Selected product not found.")
    st.stop()

selected = selected_rows.iloc[0]

col1, col2, col3 = st.columns(3)

with col1:
    qty = st.number_input(
        "Quantity",
        min_value=1,
        value=1
    )

with col2:
    discount = st.number_input(
        "Discount %",
        min_value=0.0,
        max_value=100.0,
        value=0.0
    )

with col3:
    st.write("Selling Price")
    st.write(f"R {float(selected['Selling Price']):,.2f}")

st.write("**Full Product Description:**")
st.write(selected["Description"])

if st.button("Add To Quote"):
    unit_price = float(selected["Selling Price"])
    discounted_price = unit_price * (1 - discount / 100)
    line_total = discounted_price * qty

    st.session_state.quote_items.append({
        "Identification": selected["Identification"],
        "Product": selected["Short Name"],
        "Description": selected["Description"],
        "Billing": selected["Billing"],
        "Qty": qty,
        "Discount": discount,
        "Unit Price": discounted_price,
        "Total": line_total
    })

    st.success("Product added")

# -------------------------------------------------
# QUOTE SUMMARY
# -------------------------------------------------

st.header("Quote Summary")

if st.session_state.quote_items:

    quote_df = pd.DataFrame(st.session_state.quote_items)

    edited_df = st.data_editor(
        quote_df,
        use_container_width=True,
        num_rows="dynamic",
        column_config={
            "Qty": st.column_config.NumberColumn(
                "Qty",
                min_value=1,
                step=1
            ),
            "Discount": st.column_config.NumberColumn(
                "Discount %",
                min_value=0.0,
                max_value=100.0,
                step=0.5
            ),
            "Unit Price": st.column_config.NumberColumn(
                "Unit Price",
                min_value=0.0,
                step=0.01,
                format="R %.2f"
            ),
            "Total": st.column_config.NumberColumn(
                "Total",
                disabled=True,
                format="R %.2f"
            ),
        },
        disabled=[
            "Identification",
            "Product",
            "Description",
            "Billing",
            "Total"
        ]
    )

    edited_df["Qty"] = pd.to_numeric(
        edited_df["Qty"],
        errors="coerce"
    ).fillna(1)

    edited_df["Discount"] = pd.to_numeric(
        edited_df["Discount"],
        errors="coerce"
    ).fillna(0)

    edited_df["Unit Price"] = pd.to_numeric(
        edited_df["Unit Price"],
        errors="coerce"
    ).fillna(0)

    edited_df["Total"] = (
        edited_df["Qty"]
        * edited_df["Unit Price"]
    )

    st.session_state.quote_items = edited_df.to_dict("records")

    subtotal, vat, grand_total = calculate_totals(edited_df)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Subtotal", f"R {subtotal:,.2f}")

    with col2:
        st.metric("VAT", f"R {vat:,.2f}")

    with col3:
        st.metric("Grand Total", f"R {grand_total:,.2f}")

    # -------------------------------------------------
    # GENERATE / SAVE PDF
    # -------------------------------------------------

    if st.button("Generate / Save PDF"):

        try:
            pdf_path = generate_pdf(
                quote_number=quote_number,
                customer=customer_name,
                company=company_name,
                site=site_name,
                customer_email=customer_email,
                salesperson=salesperson,
                salesperson_phone=salesperson_phone,
                salesperson_email=salesperson_email,
                quote_df=edited_df,
                subtotal=subtotal,
                vat=vat,
                total=grand_total,
                terms=terms
            )

            save_quote_json(
                quote_number=quote_number,
                customer_name=customer_name,
                company_name=company_name,
                site_name=site_name,
                customer_email=customer_email,
                salesperson=salesperson,
                salesperson_phone=salesperson_phone,
                salesperson_email=salesperson_email,
                items=edited_df.to_dict("records"),
                subtotal=subtotal,
                vat=vat,
                total=grand_total,
                pdf_path=pdf_path
            )

            st.success("Quote saved and PDF generated")

            with open(pdf_path, "rb") as f:
                st.download_button(
                    "⬇ Download PDF",
                    f,
                    file_name=f"{quote_number}.pdf",
                    mime="application/pdf"
                )

        except Exception as e:
            st.error(f"PDF generation error: {e}")

    # -------------------------------------------------
    # EMAIL PDF
    # -------------------------------------------------

    if st.button("Email Quote To Customer"):

        pdf_path = f"output/PDFs/{quote_number}.pdf"

        if not os.path.exists(pdf_path):
            st.error("Please generate/save the PDF first.")
        elif customer_email.strip() == "":
            st.error("Please enter customer email address.")
        else:
            success = send_email(
                recipient=customer_email,
                pdf_path=pdf_path,
                quote_number=quote_number
            )

            if success:
                st.success("Quote emailed successfully")
            else:
                st.error("Email failed. Check email settings in emailer.py")

else:
    st.info("No products added yet.")