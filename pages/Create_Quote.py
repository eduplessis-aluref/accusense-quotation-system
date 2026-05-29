import os
import streamlit as st
import pandas as pd

from modules.ui import render_header
from modules.auth import require_login, logout_button
import modules.google_sheets as gs

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

current_user = require_login()

render_header()

st.sidebar.success(f"Logged in as: {current_user.get('Name', '')}")
logout_button()

st.sidebar.divider()

if st.sidebar.button("🔄 Refresh Google Sheets", use_container_width=True):
    st.cache_data.clear()
    st.sidebar.success("Google Sheet data refreshed")
    st.rerun()


os.makedirs("output/PDFs", exist_ok=True)
os.makedirs("output/quotes", exist_ok=True)


@st.cache_data(ttl=300)
def get_cached_products():
    return gs.load_products()


@st.cache_data(ttl=300)
def get_cached_terms():
    return gs.load_terms()


@st.cache_data(ttl=300)
def get_cached_templates():
    return gs.load_solution_templates()


def safe_text(value):
    if value is None:
        return ""
    return str(value)


def safe_float(value, default=0):
    try:
        if value is None or value == "":
            return default

        return float(
            str(value)
            .replace("R", "")
            .replace(",", "")
            .strip()
        )

    except Exception:
        return default


defaults = {
    "quote_items": [],
    "loaded_quote_number": "",
    "base_quote_number": "",
    "revision_mode": False,
    "dashboard_template_loaded": False,
    "current_quote_number": "",
    "customer_name": "",
    "company_name": "",
    "site_name": "",
    "salesperson": safe_text(current_user.get("Name", "")),
    "salesperson_phone": safe_text(current_user.get("Phone", "")),
    "salesperson_email": safe_text(current_user.get("Email", "")),
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


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
    "Billing",
    "Final Cost before profit",
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
    .replace("", "General")
)

products_df["Short Name"] = (
    products_df["Short Name"]
    .fillna("")
    .astype(str)
    .str.strip()
)

products_df["Description"] = (
    products_df["Description"]
    .fillna("")
    .astype(str)
    .str.strip()
)

products_df["Billing"] = (
    products_df["Billing"]
    .fillna("")
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

products_df["Final Cost before profit"] = (
    products_df["Final Cost before profit"]
    .astype(str)
    .str.replace(",", "", regex=False)
    .str.replace("R", "", regex=False)
    .str.strip()
)

products_df["Final Cost before profit"] = pd.to_numeric(
    products_df["Final Cost before profit"],
    errors="coerce"
).fillna(0)

def calculate_line_values(product, qty, discount):
    unit_price = float(product["Selling Price"])
    cost_price = float(product["Final Cost before profit"])

    line_total = qty * unit_price * (1 - discount / 100)
    line_cost = qty * cost_price
    profit = line_total - line_cost

    if line_total > 0:
        profit_margin = (profit / line_total) * 100
    else:
        profit_margin = 0

    return unit_price, cost_price, line_total, line_cost, profit, profit_margin


def normalise_quote_df(df):
    required_quote_columns = [
        "Identification",
        "Product",
        "Description",
        "Billing",
        "Qty",
        "Discount",
        "Unit Price",
        "Cost Price",
        "Line Cost",
        "Total",
        "Profit",
        "Profit Margin %",
        "Locked",
        "Template",
    ]

    for col in required_quote_columns:
        if col not in df.columns:
            if col in [
                "Qty",
                "Discount",
                "Unit Price",
                "Cost Price",
                "Line Cost",
                "Total",
                "Profit",
                "Profit Margin %",
            ]:
                df[col] = 0
            else:
                df[col] = ""

    numeric_cols = [
        "Qty",
        "Discount",
        "Unit Price",
        "Cost Price",
        "Line Cost",
        "Total",
        "Profit",
        "Profit Margin %",
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    return df[required_quote_columns]


def recalculate_quote_df(df):
    df = normalise_quote_df(df.copy())

    df["Qty"] = pd.to_numeric(df["Qty"], errors="coerce").fillna(1)
    df["Discount"] = pd.to_numeric(df["Discount"], errors="coerce").fillna(0)
    df["Unit Price"] = pd.to_numeric(df["Unit Price"], errors="coerce").fillna(0)
    df["Cost Price"] = pd.to_numeric(df["Cost Price"], errors="coerce").fillna(0)

    df["Total"] = (
        df["Qty"]
        * df["Unit Price"]
        * (1 - df["Discount"] / 100)
    )

    df["Line Cost"] = df["Qty"] * df["Cost Price"]
    df["Profit"] = df["Total"] - df["Line Cost"]

    df["Profit Margin %"] = df.apply(
        lambda row: (row["Profit"] / row["Total"] * 100)
        if row["Total"] > 0 else 0,
        axis=1
    )

    return df


def quote_already_saved(quote_number):
    json_path = os.path.join(
        "output",
        "quotes",
        f"{quote_number}.json"
    )

    pdf_path = os.path.join(
        "output",
        "PDFs",
        f"{quote_number}.pdf"
    )

    return os.path.exists(json_path) or os.path.exists(pdf_path)


def add_annual_monitoring_fee(df):
    df = df.copy()

    df = df[
        df["Product"].astype(str).str.strip() != "Annual_Monitoring"
    ].copy()

    sensor_rows = df[
        df["Identification"]
        .astype(str)
        .str.lower()
        .str.contains("sensor", na=False)
    ]

    total_sensors = float(sensor_rows["Qty"].sum())

    if total_sensors <= 0:
        return df

    monitoring_products = products_df[
        products_df["Short Name"]
        .astype(str)
        .str.strip()
        == "Monitoring Fee"
    ]

    if monitoring_products.empty:
        st.warning(
            "Sensors were found, but no product called 'Monitoring Fee' exists in the Products sheet."
        )
        return df

    monitoring_product = monitoring_products.iloc[0]

    monthly_fee = float(monitoring_product["Selling Price"])
    monitoring_cost_price = float(monitoring_product["Final Cost before profit"])

    monitoring_total = total_sensors * monthly_fee * 12
    monitoring_cost = total_sensors * monitoring_cost_price * 12
    monitoring_profit = monitoring_total - monitoring_cost

    if monitoring_total > 0:
        monitoring_margin = (monitoring_profit / monitoring_total) * 100
    else:
        monitoring_margin = 0

    monitoring_row = {
        "Identification": "Service",
        "Product": "Annual_Monitoring",
        "Description": (
            f"Monitoring Fee - {int(total_sensors)} Sensors "
            f"(12 Months Prepaid)"
        ),
        "Billing": "12 Months Prepaid",
        "Qty": 1,
        "Discount": 0,
        "Unit Price": monitoring_total,
        "Cost Price": monitoring_cost,
        "Line Cost": monitoring_cost,
        "Total": monitoring_total,
        "Profit": monitoring_profit,
        "Profit Margin %": monitoring_margin,
        "Locked": "Yes",
        "Template": "Annual Monitoring"
    }

    df = pd.concat(
        [df, pd.DataFrame([monitoring_row])],
        ignore_index=True
    )

    return df

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

        identification = str(
            template_row["Identification"]
        ).strip()

        short_name = str(
            template_row["Short Name"]
        ).strip()

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
            missing_items.append(
                f"{identification} - {short_name}"
            )
            continue

        product = matched_products.iloc[0]

        (
            unit_price,
            cost_price,
            line_total,
            line_cost,
            profit,
            profit_margin,
        ) = calculate_line_values(
            product,
            qty,
            discount
        )

        st.session_state.quote_items.append(
            {
                "Identification": product["Identification"],
                "Product": product["Short Name"],
                "Description": product["Description"],
                "Billing": product["Billing"],
                "Qty": qty,
                "Discount": discount,
                "Unit Price": unit_price,
                "Cost Price": cost_price,
                "Line Cost": line_cost,
                "Total": line_total,
                "Profit": profit,
                "Profit Margin %": profit_margin,
                "Locked": locked,
                "Template": template_name,
            }
        )

        added_count += 1

    if added_count > 0:
        st.success(
            f"Loaded template: {template_name}"
        )

    if missing_items:
        st.warning(
            "These template items were not found "
            "in Products sheet: "
            + ", ".join(missing_items)
        )


query_template = st.query_params.get(
    "template",
    ""
)

session_template = st.session_state.get(
    "selected_template_from_dashboard",
    ""
)

template_to_load = (
    session_template
    or query_template
)

if (
    template_to_load
    and not st.session_state.dashboard_template_loaded
):

    load_template_into_quote(template_to_load)

    st.session_state.dashboard_template_loaded = True

    if (
        "selected_template_from_dashboard"
        in st.session_state
    ):
        del st.session_state[
            "selected_template_from_dashboard"
        ]


st.sidebar.header("Quote Options")

if st.sidebar.button("Clear Current Quote"):

    st.session_state.quote_items = []
    st.session_state.loaded_quote_number = ""
    st.session_state.base_quote_number = ""
    st.session_state.revision_mode = False
    st.session_state.dashboard_template_loaded = False
    st.session_state.current_quote_number = ""

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

        st.session_state.quote_items = (
            quote_data.get("items", [])
        )

        st.session_state.customer_name = (
            quote_data.get("customer_name", "")
        )

        st.session_state.company_name = (
            quote_data.get("company_name", "")
        )

        st.session_state.site_name = (
            quote_data.get("site_name", "")
        )

        st.session_state.salesperson = safe_text(
            quote_data.get(
                "salesperson",
                current_user.get("Name", "")
            )
        )

        st.session_state.salesperson_phone = safe_text(
            quote_data.get(
                "salesperson_phone",
                current_user.get("Phone", "")
            )
        )

        st.session_state.salesperson_email = safe_text(
            quote_data.get(
                "salesperson_email",
                current_user.get("Email", "")
            )
        )

        loaded_quote_number = quote_data.get(
            "quote_number",
            ""
        )

        st.session_state.loaded_quote_number = (
            loaded_quote_number
        )

        base_quote_number = quote_data.get(
            "base_quote_number",
            ""
        )

        if not base_quote_number:

            if "-REV" in loaded_quote_number:
                base_quote_number = (
                    loaded_quote_number
                    .split("-REV")[0]
                )

            elif "-R" in loaded_quote_number:
                base_quote_number = (
                    loaded_quote_number
                    .rsplit("-R", 1)[0]
                )

            else:
                base_quote_number = (
                    loaded_quote_number
                )

        st.session_state.base_quote_number = (
            base_quote_number
        )

        st.session_state.revision_mode = True
        st.session_state.current_quote_number = ""

        st.success(
            f"Loaded quote: {selected_saved_quote}"
        )

        st.rerun()


st.session_state.salesperson = safe_text(
    st.session_state.salesperson
)

st.session_state.salesperson_phone = safe_text(
    st.session_state.salesperson_phone
)

st.session_state.salesperson_email = safe_text(
    st.session_state.salesperson_email
)

if st.session_state.revision_mode:

    if not st.session_state.current_quote_number:

        quote_number, revision = generate_revision_quote_number(
            st.session_state.base_quote_number
        )

        st.session_state.current_quote_number = quote_number

    else:

        quote_number = st.session_state.current_quote_number

else:

    if not st.session_state.current_quote_number:

        quote_number = generate_quote_number(
            st.session_state.salesperson
        )

        st.session_state.current_quote_number = quote_number

    else:

        quote_number = st.session_state.current_quote_number


st.sidebar.write("### Quote Number")
st.sidebar.success(quote_number)


# =====================================================
# QUOTE DETAILS
# =====================================================

st.header("Quote Details")

customer_col, company_col, site_col = st.columns(3)

with customer_col:
    customer_name = st.text_input(
        "Customer Name",
        key="customer_name"
    )

with company_col:
    company_name = st.text_input(
        "Company",
        key="company_name"
    )

with site_col:
    site_name = st.text_input(
        "Site",
        key="site_name"
    )


st.subheader("Salesperson Details")

sales_col1, sales_col2, sales_col3 = st.columns(3)

with sales_col1:
    salesperson = st.text_input(
        "Salesperson Name",
        key="salesperson"
    )

with sales_col2:
    salesperson_phone = st.text_input(
        "Salesperson Phone",
        key="salesperson_phone"
    )

with sales_col3:
    salesperson_email = st.text_input(
        "Salesperson Email",
        key="salesperson_email"
    )


# =====================================================
# LOAD TEMPLATE
# =====================================================

with st.expander("📦 Load Solution Template", expanded=False):

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
            st.rerun()

    else:

        st.info(
            "No solution templates found. "
            "Add a SolutionTemplates tab in Google Sheets."
        )

# =====================================================
# ADD PRODUCTS
# =====================================================

with st.expander("➕ Add Products Manually", expanded=False):

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
                value=1,
                step=1
            )

        with col2:
            discount = st.number_input(
                "Discount %",
                min_value=0.0,
                max_value=100.0,
                value=0.0,
                step=0.5
            )

        with col3:
            st.write("Selling Price")
            st.write(f"R {float(selected['Selling Price']):,.2f}")


        st.write("**Full Product Description:**")
        st.write(selected["Description"])


        if st.button("Add To Quote"):

            (
                unit_price,
                cost_price,
                line_total,
                line_cost,
                profit,
                profit_margin,
            ) = calculate_line_values(
                selected,
                qty,
                discount
            )

            st.session_state.quote_items.append(
                {
                    "Identification": selected["Identification"],
                    "Product": selected["Short Name"],
                    "Description": selected["Description"],
                    "Billing": selected["Billing"],
                    "Qty": qty,
                    "Discount": discount,
                    "Unit Price": unit_price,
                    "Cost Price": cost_price,
                    "Line Cost": line_cost,
                    "Total": line_total,
                    "Profit": profit,
                    "Profit Margin %": profit_margin,
                    "Locked": "No",
                    "Template": "",
                }
            )

            st.success("Product added")
            st.rerun()


# =====================================================
# QUOTE SUMMARY
# =====================================================

st.header("Quote Summary")

if st.session_state.quote_items:

    quote_df = pd.DataFrame(
        st.session_state.quote_items
    )

    quote_df = normalise_quote_df(quote_df)

    quote_df = quote_df[
        quote_df["Product"]
        .astype(str)
        .str.strip()
        != "Annual_Monitoring"
    ].copy()

    edited_df = st.data_editor(
        quote_df,
        use_container_width=True,
        num_rows="dynamic"
    )

    edited_df = recalculate_quote_df(edited_df)

    st.session_state.quote_items = (
        edited_df.to_dict("records")
    )

    final_df = add_annual_monitoring_fee(
        edited_df
    )

    final_df = recalculate_quote_df(
        final_df
    )

    subtotal, vat, grand_total = calculate_totals(
        final_df
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


    # =====================================================
    # APPROVAL LOGIC
    # =====================================================

    can_approve = (
        str(current_user.get("Can Approve", "No"))
        .strip()
        .lower()
        == "yes"
    )

    approval_limit_raw = str(
        current_user.get("Approval Limit")
        or ""
    ).strip()

    if approval_limit_raw == "":

        if can_approve:
            user_approval_limit = float("inf")
        else:
            user_approval_limit = 0

    else:

        user_approval_limit = safe_float(
            approval_limit_raw,
            0
        )

    approval_required = (
        grand_total > user_approval_limit
    )

    approve_quote = False

    if approval_required:

        st.error(
            f"Approval required. "
            f"Quote total is R {grand_total:,.2f}, "
            f"but your approval limit is "
            f"R {user_approval_limit:,.2f}."
        )

        if can_approve:

            approve_quote = st.checkbox(
                "Approve this quote"
            )

        else:

            st.warning(
                "You are not authorised to approve this quote."
            )

    else:

        approve_quote = True


    approval_status = gs.get_quote_approval_status(
        quote_number
    )

    if approval_status:

        status = str(
            approval_status.get("Status", "")
        ).strip().lower()

        if status == "pending":

            st.warning(
                "This quote is awaiting approval."
            )

        elif status == "rejected":

            st.error(
                "This quote was rejected."
            )

            rejection_notes = approval_status.get(
                "Notes",
                ""
            )

            if rejection_notes:

                st.write(
                    f"Reason: {rejection_notes}"
                )

        elif status == "approved":

            st.success(
                f"Quote approved by "
                f"{approval_status.get('Approved By', '')}"
            )


    already_saved = quote_already_saved(
        quote_number
    )

    if already_saved:

        st.warning(
            "This quote has already been generated and saved."
        )

    else:

        required_fields_missing = (
            not customer_name.strip()
            or not company_name.strip()
            or not salesperson.strip()
        )

        if required_fields_missing:

            st.error(
                "Customer Name, Company and Salesperson "
                "are required before saving a quote."
            )

        if st.button("Generate / Save PDF"):

            if required_fields_missing:
                st.stop()

            if not approve_quote:

                saved_json_path = save_quote_json(
                    quote_number=quote_number,
                    customer_name=customer_name,
                    company_name=company_name,
                    site_name=site_name,
                    customer_email="",
                    salesperson=salesperson,
                    salesperson_phone=salesperson_phone,
                    salesperson_email=salesperson_email,
                    items=final_df.to_dict("records"),
                    subtotal=subtotal,
                    vat=vat,
                    total=grand_total,
                    pdf_path=""
                )

                approval_saved = gs.save_approval_request(
                    quote_number=quote_number,
                    customer=customer_name,
                    company=company_name,
                    salesperson=salesperson,
                    salesperson_email=salesperson_email,
                    quote_total=grand_total,
                    approval_limit=user_approval_limit,
                )

                if approval_saved:

                    st.error(
                        "This quote exceeds your approval limit. "
                        "An approval request has been submitted."
                    )

                    st.info(
                        "Quote detail saved for approval review: "
                        f"{saved_json_path}"
                    )

                else:

                    st.error(
                        "Approval request could not be submitted."
                    )

                st.stop()

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
                    quote_df=final_df,
                    subtotal=subtotal,
                    vat=vat,
                    total=grand_total,
                    terms=terms,
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
                    items=final_df.to_dict("records"),
                    subtotal=subtotal,
                    vat=vat,
                    total=grand_total,
                    pdf_path=pdf_path,
                )

                st.success(
                    "Quote saved successfully."
                )

                if os.path.exists(pdf_path):

                    with open(pdf_path, "rb") as f:

                        st.download_button(
                            "⬇ Download PDF",
                            f,
                            file_name=f"{quote_number}.pdf",
                            mime="application/pdf",
                        )

            except Exception as e:

                import traceback

                st.error(str(e))
                st.code(traceback.format_exc())

else:

    st.info("No products added yet.")