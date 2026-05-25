IndentationError: This app has encountered an error. The original error message is redacted to prevent data leaks. Full error details have been recorded in the logs (if you're on Streamlit Cloud, click on 'Manage app' in the lower right of your app).
Traceback:
File "/home/adminuser/venv/lib/python3.14/site-packages/streamlit/runtime/scriptrunner/exec_code.py", line 129, in exec_func_with_error_handling
    result = func()
File "/home/adminuser/venv/lib/python3.14/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 687, in code_to_exec
    _mpa_v1(self._main_script_path)
    ~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^
File "/home/adminuser/venv/lib/python3.14/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 166, in _mpa_v1
    page.run()
    ~~~~~~~~^^
File "/home/adminuser/venv/lib/python3.14/site-packages/streamlit/navigation/page.py", line 486, in run
    code = ctx.pages_manager.get_page_script_byte_code(str(self._page))
File "/home/adminuser/venv/lib/python3.14/site-packages/streamlit/runtime/pages_manager.py", line 160, in get_page_script_byte_code
    return self._script_cache.get_bytecode(script_path)
           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^
File "/home/adminuser/venv/lib/python3.14/site-packages/streamlit/runtime/scriptrunner/script_cache.py", line 72, in get_bytecode
    filebody = magic.add_magic(filebody, script_path)
File "/home/adminuser/venv/lib/python3.14/site-packages/streamlit/runtime/scriptrunner/magic.py", line 45, in add_magic
    tree = ast.parse(code, script_path, "exec")
File "/usr/local/lib/python3.14/ast.py", line 46, in parse
    return compile(source, filename, mode, flags,
                   _feature_version=feature_version, optimize=optimize)

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

        unit_price, cost_price, line_total, line_cost, profit, profit_margin = (
            calculate_line_values(product, qty, discount)
        )

        st.session_state.quote_items.append({
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
session_template = st.session_state.get("selected_template_from_dashboard", "")

template_to_load = session_template or query_template

if template_to_load and not st.session_state.dashboard_template_loaded:
    load_template_into_quote(template_to_load)
    st.session_state.dashboard_template_loaded = True

    if "selected_template_from_dashboard" in st.session_state:
        del st.session_state.selected_template_from_dashboard


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
        quote_data = load_quote_json(selected_saved_quote)

        st.session_state.quote_items = quote_data.get("items", [])

        st.session_state.customer_name = quote_data.get("customer_name", "")
        st.session_state.company_name = quote_data.get("company_name", "")
        st.session_state.site_name = quote_data.get("site_name", "")

        st.session_state.salesperson = safe_text(
            quote_data.get("salesperson", current_user.get("Name", ""))
        )

        st.session_state.salesperson_phone = safe_text(
            quote_data.get("salesperson_phone", current_user.get("Phone", ""))
        )

        st.session_state.salesperson_email = safe_text(
            quote_data.get("salesperson_email", current_user.get("Email", ""))
        )

        loaded_quote_number = quote_data.get("quote_number", "")
        st.session_state.loaded_quote_number = loaded_quote_number

        base_quote_number = quote_data.get("base_quote_number", "")

        if not base_quote_number:
            if "-REV" in loaded_quote_number:
                base_quote_number = loaded_quote_number.split("-REV")[0]
            elif "-R" in loaded_quote_number:
                base_quote_number = loaded_quote_number.rsplit("-R", 1)[0]
            else:
                base_quote_number = loaded_quote_number

        st.session_state.base_quote_number = base_quote_number
        st.session_state.revision_mode = True
        st.session_state.current_quote_number = ""

        st.success(f"Loaded quote: {selected_saved_quote}")
        st.rerun()


st.sidebar.header("Customer Details")

customer_name = st.sidebar.text_input(
    "Customer Name",
    key="customer_name"
)

company_name = st.sidebar.text_input(
    "Company",
    key="company_name"
)

site_name = st.sidebar.text_input(
    "Site",
    key="site_name"
)


st.session_state.salesperson = safe_text(st.session_state.salesperson)
st.session_state.salesperson_phone = safe_text(st.session_state.salesperson_phone)
st.session_state.salesperson_email = safe_text(st.session_state.salesperson_email)

st.sidebar.header("Salesperson Details")

salesperson = st.sidebar.text_input(
    "Salesperson Name",
    key="salesperson"
)

salesperson_phone = st.sidebar.text_input(
    "Salesperson Phone",
    key="salesperson_phone"
)

salesperson_email = st.sidebar.text_input(
    "Salesperson Email",
    key="salesperson_email"
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
        quote_number = generate_quote_number(salesperson)
        st.session_state.current_quote_number = quote_number
    else:
        quote_number = st.session_state.current_quote_number


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
        st.rerun()

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
    unit_price, cost_price, line_total, line_cost, profit, profit_margin = (
        calculate_line_values(selected, qty, discount)
    )

    st.session_state.quote_items.append({
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
        "Template": ""
    })

    st.success("Product added")
    st.rerun()
st.header("Quote Summary")

if st.session_state.quote_items:

    quote_df = pd.DataFrame(st.session_state.quote_items)
    quote_df = normalise_quote_df(quote_df)

    quote_df = quote_df[
        quote_df["Product"].astype(str).str.strip() != "Annual_Monitoring"
    ].copy()

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

            "Cost Price": st.column_config.NumberColumn(
                "Cost Price",
                disabled=True,
                format="R %.2f",
                width="medium"
            ),

            "Line Cost": st.column_config.NumberColumn(
                "Line Cost",
                disabled=True,
                format="R %.2f",
                width="medium"
            ),

            "Total": st.column_config.NumberColumn(
                "Total",
                disabled=True,
                format="R %.2f",
                width="medium"
            ),

            "Profit": st.column_config.NumberColumn(
                "Profit",
                disabled=True,
                format="R %.2f",
                width="medium"
            ),

            "Profit Margin %": st.column_config.NumberColumn(
                "Profit Margin %",
                disabled=True,
                format="%.1f %%",
                width="medium"
            ),
        },
        disabled=[
            "Identification",
            "Product",
            "Description",
            "Billing",
            "Cost Price",
            "Line Cost",
            "Total",
            "Profit",
            "Profit Margin %",
            "Locked",
            "Template"
        ]
    )

    edited_df = recalculate_quote_df(edited_df)

    st.session_state.quote_items = edited_df.to_dict("records")

    final_df = add_annual_monitoring_fee(edited_df)
    final_df = recalculate_quote_df(final_df)

    if len(final_df) != len(edited_df):
        st.subheader("Final Quote Lines Including Annual Monitoring")
        st.dataframe(
            final_df,
            use_container_width=True,
            hide_index=True
        )

    subtotal, vat, grand_total = calculate_totals(final_df)

    gross_profit = float(final_df["Profit"].sum())
    total_cost = float(final_df["Line Cost"].sum())

    if subtotal > 0:
        gross_margin = (gross_profit / subtotal) * 100
    else:
        gross_margin = 0

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Subtotal", f"R {subtotal:,.2f}")

    with col2:
        st.metric("VAT", f"R {vat:,.2f}")

    with col3:
        st.metric("Grand Total", f"R {grand_total:,.2f}")

    with col4:
        st.metric("Gross Profit", f"R {gross_profit:,.2f}")

    st.caption(
        f"Total Cost: R {total_cost:,.2f} | Gross Margin: {gross_margin:.1f}%"
    )


    # =====================================================
    # APPROVAL LOGIC
    # =====================================================

    approval_limit_raw = str(
        current_user.get("Approval Limit", "")
    ).strip()

    if approval_limit_raw == "":
        user_approval_limit = float("inf")
    else:
        user_approval_limit = safe_float(
            approval_limit_raw,
            0
        )

    can_approve = (
        str(current_user.get("Can Approve", "No"))
        .strip()
        .lower()
        == "yes"
    )

    approval_required = grand_total > user_approval_limit

    approve_quote = False

    if approval_required:

        st.error(
            f"Approval required. "
            f"Quote total is R {grand_total:,.2f}, "
            f"but your approval limit is R {user_approval_limit:,.2f}."
        )

        if can_approve:

            st.success("You are authorised to approve this quote.")

            approve_quote = st.checkbox(
                "Approve this quote"
            )

        else:

            st.warning("You are not authorised to approve this quote.")

    else:

        approve_quote = True


    # =====================================================
    # GENERATE / SAVE PDF
    # =====================================================

    already_saved = quote_already_saved(quote_number)

    if already_saved:

        st.warning(
            "This quote has already been generated and saved. "
            "To create a changed version, load it as a revision or clear the current quote."
        )

        existing_pdf_path = os.path.join(
            "output",
            "PDFs",
            f"{quote_number}.pdf"
        )

        if os.path.exists(existing_pdf_path):

            with open(existing_pdf_path, "rb") as f:

                st.download_button(
                    "⬇ Download Existing PDF",
                    f,
                    file_name=f"{quote_number}.pdf",
                    mime="application/pdf"
                )

    else:

        if st.button("Generate / Save PDF"):

            if not approve_quote:

                st.error(
                    "This quote cannot be generated until it is approved."
                )

                st.stop()

            try:

                st.info("Starting PDF generation...")

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
                    terms=terms
                )

                st.success(
                    f"PDF generated successfully: {pdf_path}"
                )

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
                    pdf_path=pdf_path
                )

                st.success(
                    f"Quote JSON saved successfully: {saved_json_path}"
                )

                st.write("PDF saved to:")
                st.code(pdf_path)

                st.write("Quote data saved to:")
                st.code(saved_json_path)

                if os.path.exists(pdf_path):

                    with open(pdf_path, "rb") as f:

                        st.download_button(
                            "⬇ Download PDF",
                            f,
                            file_name=f"{quote_number}.pdf",
                            mime="application/pdf"
                        )

                else:

                    st.error("PDF file was not found after generation.")

            except Exception as e:

                import traceback

                st.error("Quote save failed.")
                st.error(str(e))
                st.code(traceback.format_exc())

else:
    st.info("No products added yet.")