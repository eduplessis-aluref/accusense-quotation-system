import pandas as pd
import streamlit as st

from modules.ui import render_header
from modules.auth import require_login, logout_button


st.set_page_config(
    page_title="Sales Report",
    layout="wide"
)

current_user = require_login()

render_header()

st.sidebar.success(f"Logged in as: {current_user.get('Name', '')}")
logout_button()

st.sidebar.divider()

if st.sidebar.button("🔄 Refresh Report Data", use_container_width=True):
    st.cache_data.clear()
    st.sidebar.success("Report data refreshed")
    st.rerun()


def money(value):
    try:
        return "R " + f"{float(value):,.2f}".replace(",", " ")
    except Exception:
        return "R 0.00"


def percent(value):
    try:
        return f"{float(value):.1f}%"
    except Exception:
        return "0.0%"

from modules.quote_logic import get_spreadsheet

@st.cache_data(ttl=300)
def load_quote_data():

    spreadsheet = get_spreadsheet()

    register_sheet = spreadsheet.worksheet("QuoteRegister")
    items_sheet = spreadsheet.worksheet("QuoteItems")

    register_rows = register_sheet.get_all_records()
    item_rows = items_sheet.get_all_records()

    register_df = pd.DataFrame(register_rows)
    items_df = pd.DataFrame(item_rows)

    if register_df.empty:
        return pd.DataFrame()

    if items_df.empty:
        register_df["Total Cost"] = 0
        register_df["Gross Profit"] = 0
        register_df["Gross Margin %"] = 0
        register_df["Template"] = ""
        return register_df

    numeric_cols = [
        "Line Cost",
        "Profit",
        "Total"
    ]

    for col in numeric_cols:

        if col not in items_df.columns:
            items_df[col] = 0

        items_df[col] = pd.to_numeric(
            items_df[col],
            errors="coerce"
        ).fillna(0)

    if "Template" not in items_df.columns:
        items_df["Template"] = ""

    item_summary = (
        items_df
        .groupby("Quote Number", dropna=False)
        .agg({
            "Line Cost": "sum",
            "Profit": "sum",
            "Template": "first"
        })
        .reset_index()
        .rename(columns={
            "Line Cost": "Total Cost",
            "Profit": "Gross Profit"
        })
    )

    report_df = register_df.merge(
        item_summary,
        on="Quote Number",
        how="left"
    )

    report_df["Subtotal"] = pd.to_numeric(
        report_df["Subtotal"],
        errors="coerce"
    ).fillna(0)

    report_df["VAT"] = pd.to_numeric(
        report_df["VAT"],
        errors="coerce"
    ).fillna(0)

    report_df["Total"] = pd.to_numeric(
        report_df["Total"],
        errors="coerce"
    ).fillna(0)

    report_df["Total Cost"] = pd.to_numeric(
        report_df["Total Cost"],
        errors="coerce"
    ).fillna(0)

    report_df["Gross Profit"] = pd.to_numeric(
        report_df["Gross Profit"],
        errors="coerce"
    ).fillna(0)

    report_df["Gross Margin %"] = report_df.apply(
        lambda row: (
            row["Gross Profit"] / row["Subtotal"] * 100
        ) if row["Subtotal"] > 0 else 0,
        axis=1
    )

    return report_df


st.title("Sales Report")

df = load_quote_data()

if df.empty:
    st.warning("No saved quote data found yet.")
    st.stop()


st.sidebar.header("Report Filters")

salespeople = sorted(df["Salesperson"].dropna().astype(str).unique())
templates = sorted(df["Template"].dropna().astype(str).unique())

selected_salesperson = st.sidebar.selectbox(
    "Salesperson",
    ["All"] + salespeople
)

selected_template = st.sidebar.selectbox(
    "Solution Template",
    ["All"] + templates
)

filtered_df = df.copy()

if selected_salesperson != "All":
    filtered_df = filtered_df[
        filtered_df["Salesperson"] == selected_salesperson
    ]

if selected_template != "All":
    filtered_df = filtered_df[
        filtered_df["Template"] == selected_template
    ]


total_sales = filtered_df["Subtotal"].sum()
total_vat = filtered_df["VAT"].sum()
grand_total = filtered_df["Total"].sum()
gross_profit = filtered_df["Gross Profit"].sum()
total_cost = filtered_df["Total Cost"].sum()
quote_count = len(filtered_df)

if total_sales > 0:
    gross_margin = (gross_profit / total_sales) * 100
else:
    gross_margin = 0


col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Quotes", quote_count)

with col2:
    st.metric("Sales Excl. VAT", f"R {total_sales:,.2f}")

with col3:
    st.metric("Gross Profit", f"R {gross_profit:,.2f}")

with col4:
    st.metric("Gross Margin", f"{gross_margin:.1f}%")


col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Cost", f"R {total_cost:,.2f}")

with col2:
    st.metric("VAT", f"R {total_vat:,.2f}")

with col3:
    st.metric("Total Incl. VAT", f"R {grand_total:,.2f}")


st.divider()

st.subheader("Sales by Salesperson")

salesperson_summary = (
    filtered_df
    .groupby("Salesperson", dropna=False)
    .agg({
        "Quote Number": "count",
        "Subtotal": "sum",
        "Gross Profit": "sum",
        "Total": "sum"
    })
    .reset_index()
)

salesperson_summary = salesperson_summary.rename(
    columns={
        "Quote Number": "Quotes",
        "Subtotal": "Sales Excl. VAT"
    }
)

salesperson_summary["Gross Margin %"] = salesperson_summary.apply(
    lambda row: (row["Gross Profit"] / row["Sales Excl. VAT"] * 100)
    if row["Sales Excl. VAT"] > 0 else 0,
    axis=1
)

salesperson_display = salesperson_summary.copy()

for col in ["Sales Excl. VAT", "Gross Profit", "Total"]:
    salesperson_display[col] = salesperson_display[col].apply(money)

salesperson_display["Gross Margin %"] = (
    salesperson_display["Gross Margin %"].apply(percent)
)

st.dataframe(
    salesperson_display,
    use_container_width=True,
    hide_index=True
)

st.subheader("Sales by Template")

template_summary = (
    filtered_df
    .groupby("Template", dropna=False)
    .agg({
        "Quote Number": "count",
        "Subtotal": "sum",
        "Gross Profit": "sum",
        "Total": "sum"
    })
    .reset_index()
)

template_summary = template_summary.rename(
    columns={
        "Quote Number": "Quotes",
        "Subtotal": "Sales Excl. VAT"
    }
)

template_summary["Gross Margin %"] = template_summary.apply(
    lambda row: (row["Gross Profit"] / row["Sales Excl. VAT"] * 100)
    if row["Sales Excl. VAT"] > 0 else 0,
    axis=1
)

template_display = template_summary.copy()

for col in ["Sales Excl. VAT", "Gross Profit", "Total"]:
    template_display[col] = template_display[col].apply(money)

template_display["Gross Margin %"] = (
    template_display["Gross Margin %"].apply(percent)
)

st.dataframe(
    template_display,
    use_container_width=True,
    hide_index=True
)


st.subheader("Quote Register Report")

display_cols = [
    "Quote Number",
    "Customer",
    "Company",
    "Salesperson",
    "Subtotal",
    "VAT",
    "Total",
    "Total Cost",
    "Gross Profit",
    "Gross Margin %",
    "Template"
]

available_cols = [
    col for col in display_cols
    if col in filtered_df.columns
]

register_display = filtered_df[available_cols].copy()

for col in [
    "Subtotal",
    "VAT",
    "Total",
    "Total Cost",
    "Gross Profit"
]:
    if col in register_display.columns:
        register_display[col] = register_display[col].apply(money)

if "Gross Margin %" in register_display.columns:
    register_display["Gross Margin %"] = (
        register_display["Gross Margin %"].apply(percent)
    )

st.dataframe(
    register_display,
    use_container_width=True,
    hide_index=True
)


csv = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    "⬇ Download Report CSV",
    csv,
    file_name="sales_report.csv",
    mime="text/csv"
)