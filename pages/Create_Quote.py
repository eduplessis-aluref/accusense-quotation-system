import os
import streamlit as st
import pandas as pd

from modules.google_sheets import load_products, load_terms

from modules.quote_logic import (
    generate_quote_number,
    generate_revision_quote_number,
    calculate_totals,
    save_quote_json,
    load_saved_quotes,
    load_quote_json,
)

from modules.pdf_generator import generate_pdf


st.set_page_config(
    page_title="AccuSense Quotation System",
    layout="wide"
)

st.title("📄 AccuSense Quotation System")


os.makedirs("output/PDFs", exist_ok=True)


@st.cache_data(ttl=300)
def get_cached_products():
    return load_products()


@st.cache_data(ttl=300)
def get_cached_terms():
    return load_terms()


if "quote_items" not in st.session_state:
    st.session_state.quote_items = []

if "loaded_quote_number" not in st.session_state:
    st.session_state.loaded_quote_number = ""

if "base_quote_number" not in st.session_state:
    st.session_state.base_quote_number = ""

if "revision_mode" not in st.session_state:
    st.session_state.revision_mode = False


try:
    products_df = get_cached_products()
    terms = get_cached_terms()

except Exception as e:

    import traceback

    st.error(str(e))
    st.code(traceback.format_exc())
    st.stop()


# =====================================================
# LOAD PREVIOUS QUOTES
# =====================================================

st.sidebar.header("Quote Options")

saved_quotes = load_saved_quotes()

selected_saved_quote = st.sidebar.selectbox(
    "Load Existing Quote",
    [""] + saved_quotes
)

if st.sidebar.button("Load Quote"):

    if selected_saved_quote:

        quote_data = load_quote_json(
            selected_saved_quote
        )

        st.session_state.quote_items = quote_data["items"]

        st.session_state.customer_name = quote_data["customer_name"]
        st.session_state.company_name = quote_data["company_name"]
        st.session_state.site_name = quote_data["site_name"]

        st.session_state.salesperson = quote_data["salesperson"]

        st.session_state.loaded_quote_number = quote_data["quote_number"]

        st.session_state.base_quote_number = (
            quote_data["base_quote_number"]
        )

        st.session_state.revision_mode = True

        st.success(
            f"Loaded quote: {selected_saved_quote}"
        )


# =====================================================
# CUSTOMER DETAILS
# =====================================================

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


# =====================================================
# SALESPERSON
# =====================================================

st.sidebar.header("Salesperson Details")

salesperson = st.sidebar.text_input(
    "Salesperson Name",
    value=st.session_state.get(
        "salesperson",
        "Eddie du Plessis"
    )
)

salesperson_phone = st.sidebar.text_input(
    "Salesperson Phone",
    value=st.session_state.get(
        "salesperson_phone",
        ""
    )
)

salesperson_email = st.sidebar.text_input(
    "Salesperson Email",
    value=st.session_state.get(
        "salesperson_email",
        ""
    )
)


# =====================================================
# QUOTE NUMBER
# =====================================================

if st.session_state.revision_mode:

    quote_number, revision = (
        generate_revision_quote_number(
            st.session_state.base_quote_number
        )
    )

else:

    quote_number = generate_quote_number(
        salesperson
    )

st.sidebar.write("### Quote Number")
st.sidebar.success(quote_number)


# =====================================================
# PRODUCT SELECTION
# =====================================================

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
    products_df["Identification"]
    == selected_identification
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
    category_df["Short Name"]
    == selected_short_name
]

if not selected_rows.empty:

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

        st.write(
            f"R {float(selected['Selling Price']):,.2f}"
        )

    st.write("**Full Product Description:**")
    st.write(selected["Description"])

    if st.button("Add To Quote"):

        unit_price = float(
            selected["Selling Price"]
        )

        line_total = (
            qty
            * unit_price
            * (1 - discount / 100)
        )

        st.session_state.quote_items.append({

            "Identification":
                selected["Identification"],

            "Product":
                selected["Short Name"],

            "Description":
                selected["Description"],

            "Billing":
                selected["Billing"],

            "Qty":
                qty,

            "Discount":
                discount,

            "Unit Price":
                unit_price,

            "Total":
                line_total
        })

        st.success("Product added")


# =====================================================
# QUOTE TABLE
# =====================================================

st.header("Quote Summary")

if st.session_state.quote_items:

    quote_df = pd.DataFrame(
        st.session_state.quote_items
    )

    edited_df = st.data_editor(
        quote_df,
        use_container_width=True,
        num_rows="dynamic",
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
        * (1 - edited_df["Discount"] / 100)
    )

    st.session_state.quote_items = (
        edited_df.to_dict("records")
    )

    subtotal, vat, grand_total = (
        calculate_totals(edited_df)
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Subtotal",
            f"R {subtotal:,.2f}"
        )

    with col2:
        st.metric(
            "VAT",
            f"R {vat:,.2f}"
        )

    with col3:
        st.metric(
            "Grand Total",
            f"R {grand_total:,.2f}"
        )

    # =================================================
    # GENERATE PDF
    # =================================================

    if st.button("Generate / Save PDF"):

        try:

            pdf_path = generate_pdf(
                quote_number=quote_number,
                customer=customer_name,
                company=company_name,
                site=site_name,
                customer_email="",
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
                customer_email="",
                salesperson=salesperson,
                salesperson_phone=salesperson_phone,
                salesperson_email=salesperson_email,
                items=edited_df.to_dict("records"),
                subtotal=subtotal,
                vat=vat,
                total=grand_total,
                pdf_path=pdf_path
            )

            st.success(
                "Quote saved successfully"
            )

            with open(pdf_path, "rb") as f:

                st.download_button(
                    "⬇ Download PDF",
                    f,
                    file_name=f"{quote_number}.pdf",
                    mime="application/pdf"
                )

        except Exception as e:

            import traceback

            st.error(str(e))
            st.code(traceback.format_exc())

else:

    st.info("No products added yet.")