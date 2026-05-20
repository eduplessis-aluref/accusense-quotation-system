import os
import streamlit as st
import pandas as pd

from modules.ui import render_header
from modules.google_sheets import (
    load_products,
    load_terms,
    load_solution_templates
)
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
    page_title="Create Quote",
    layout="wide"
)

render_header()

st.markdown("""
<style>

/* Sidebar page navigation buttons */
[data-testid="stSidebarNav"] {
    background-color: #F7F9FC;
    padding-top: 10px;
}

/* Navigation links */
[data-testid="stSidebarNav"] a {
    background-color: white;
    border-radius: 10px;
    margin-bottom: 8px;
    padding: 10px 14px;
    border: 1px solid #DCE3EC;
    font-weight: 700 !important;
    font-size: 16px !important;
    color: #0B4F9C !important;
    transition: 0.15s ease-in-out;
}

/* Hover effect */
[data-testid="stSidebarNav"] a:hover {
    background-color: #EEF5FF;
    border-color: #0B4F9C;
    transform: translateX(2px);
}

/* Active page */
[data-testid="stSidebarNav"] a[aria-current="page"] {
    background-color: #0B4F9C;
    color: white !important;
    border-color: #0B4F9C;
}

</style>
""", unsafe_allow_html=True)

os.makedirs("output/PDFs", exist_ok=True)


@st.cache_data(ttl=300)
def get_cached_products():
    return load_products()


@st.cache_data(ttl=300)
def get_cached_terms():
    return load_terms()


@st.cache_data(ttl=300)
def get_cached_templates():
    return load_solution_templates()


if "quote_items" not in st.session_state:
    st.session_state.quote_items = []

if "loaded_quote_number" not in st.session_state:
    st.session_state.loaded_quote_number = ""

if "base_quote_number" not in st.session_state:
    st.session_state.base_quote_number = ""

if "revision_mode" not in st.session_state:
    st.session_state.revision_mode = False

if "dashboard_template_loaded" not in st.session_state:
    st.session_state.dashboard_template_loaded = False


try:
    products_df = get_cached_products()
    terms = get_cached_terms()
    templates_df = get_cached_templates()

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


products_df["Identification"] = (
    products_df["Identification"]
    .fillna("General")
    .astype(str)
    .str.strip()
)

products_df["Identification"] = (
    products_df["Identification"]
    .replace("", "General")
)

products_df["Short Name"] = (
    products_df["Short Name"]
    .astype(str)
    .str.strip()
)

products_df["Description"] = (
    products_df["Description"]
    .astype(str)
    .str.strip()
)

products_df["Billing"] = (
    products_df["Billing"]
    .astype(str)
    .str.strip()
)

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


def load_template_into_quote(template_name):

    if templates_df.empty:
        st.warning("No solution templates found.")
        return

    template_lines = templates_df[
        templates_df["Template Name"] == template_name
    ].copy()

    if template_lines.empty:
        st.warning(f"Template not found: {template_name}")
        return

    added_count = 0
    missing_items = []

    for _, template_row in template_lines.iterrows():

        identification = str(template_row["Identification"]).strip()
        short_name = str(template_row["Short Name"]).strip()
        qty = float(template_row["Qty"])
        discount = float(template_row["Discount"])
        locked = str(template_row["Locked"]).strip()

        matched_products = products_df[
            (
                products_df["Identification"]
                .astype(str)
                .str.strip()
                == identification
            )
            &
            (
                products_df["Short Name"]
                .astype(str)
                .str.strip()
                == short_name
            )
        ]

        if matched_products.empty:
            missing_items.append(f"{identification} - {short_name}")
            continue

        product = matched_products.iloc[0]
        unit_price = float(product["Selling Price"])

        line_total = (
            qty
            * unit_price
            * (1 - discount / 100)
        )

        st.session_state.quote_items.append({
            "Identification": product["Identification"],
            "Product": product["Short Name"],
            "Description": product["Description"],
            "Billing": product["Billing"],
            "Qty": qty,
            "Discount": discount,
            "Unit Price": unit_price,
            "Total": line_total,
            "Locked": locked,
            "Template": template_name
        })

        added_count += 1

    if added_count > 0:
        st.success(f"Loaded template: {template_name}")

    if missing_items:
        st.warning(
            "These template items were not found in Products sheet: "
            + ", ".join(missing_items)
        )


query_template = st.query_params.get("template", "")

if query_template and not st.session_state.dashboard_template_loaded:
    load_template_into_quote(query_template)
    st.session_state.dashboard_template_loaded = True


st.sidebar.header("Quote Options")

if st.sidebar.button("Clear Current Quote"):
    st.session_state.quote_items = []
    st.session_state.loaded_quote_number = ""
    st.session_state.base_quote_number = ""
    st.session_state.revision_mode = False
    st.session_state.dashboard_template_loaded = False
    st.rerun()


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


if st.session_state.revision_mode:
    quote_number, revision = generate_revision_quote_number(
        st.session_state.base_quote_number
    )
else:
    quote_number = generate_quote_number(
        salesperson
    )


st.sidebar.write("### Quote Number")
st.sidebar.success(quote_number)


st.header("Load Solution Template")

if not templates_df.empty:

    template_names = sorted(
        templates_df["Template Name"]
        .dropna()
        .astype(str)
        .unique()
    )

    selected_template = st.selectbox(
        "Select Solution Template",
        [""] + template_names
    )

    if st.button("Load Template Into Quote") and selected_template:
        load_template_into_quote(selected_template)

else:
    st.info(
        "No solution templates found. Add a SolutionTemplates tab in Google Sheets."
    )


st.header("Add Products Manually")

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
    st.write(
        f"R {float(selected['Selling Price']):,.2f}"
    )


st.write("**Full Product Description:**")
st.write(selected["Description"])


if st.button("Add To Quote"):

    unit_price = float(selected["Selling Price"])

    line_total = (
        qty
        * unit_price
        * (1 - discount / 100)
    )

    st.session_state.quote_items.append({
        "Identification": selected["Identification"],
        "Product": selected["Short Name"],
        "Description": selected["Description"],
        "Billing": selected["Billing"],
        "Qty": qty,
        "Discount": discount,
        "Unit Price": unit_price,
        "Total": line_total,
        "Locked": "No",
        "Template": ""
    })

    st.success("Product added")


st.header("Quote Summary")

if st.session_state.quote_items:

    quote_df = pd.DataFrame(
        st.session_state.quote_items
    )

    st.markdown("""
    <style>
    [data-testid="stDataFrame"] table {
        font-size: 13px;
    }

    [data-testid="stDataFrame"] table td:nth-child(8),
    [data-testid="stDataFrame"] table td:nth-child(9),
    [data-testid="stDataFrame"] table th:nth-child(8),
    [data-testid="stDataFrame"] table th:nth-child(9) {
        text-align: right !important;
    }
    </style>
    """, unsafe_allow_html=True)

    edited_df = st.data_editor(
        quote_df,
        use_container_width=True,
        num_rows="dynamic",
        column_config={

            "Qty": st.column_config.NumberColumn(
                "Qty",
                min_value=1,
                step=1,
                width="small"
            ),

            "Discount": st.column_config.NumberColumn(
                "Discount %",
                min_value=0.0,
                max_value=100.0,
                step=0.5,
                width="small",
                format="%.1f %%"
            ),

            "Unit Price": st.column_config.NumberColumn(
                "Unit Price",
                min_value=0.0,
                step=0.01,
                format="R %.2f",
                width="medium"
            ),

            "Total": st.column_config.NumberColumn(
                "Total",
                disabled=True,
                format="R %.2f",
                width="medium"
            ),

        },
        disabled=[
            "Identification",
            "Product",
            "Description",
            "Billing",
            "Total",
            "Locked",
            "Template"
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

    subtotal, vat, grand_total = calculate_totals(
        edited_df
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

            st.success("Quote saved successfully")

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