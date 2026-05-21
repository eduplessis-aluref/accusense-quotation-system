import os
import json
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


QUOTE_FOLDER = "output/quotes"


@st.cache_data(ttl=300)
def load_quote_data():

    all_quotes = []

    if not os.path.exists(QUOTE_FOLDER):
        return pd.DataFrame()

    for filename in os.listdir(QUOTE_FOLDER):

        if not filename.endswith(".json"):
            continue

        file_path = os.path.join(QUOTE_FOLDER, filename)

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                quote = json.load(f)

            quote_number = quote.get("quote_number", "")
            customer = quote.get("customer_name", "")
            company = quote.get("company_name", "")
            site = quote.get("site_name", "")
            salesperson = quote.get("salesperson", "")
            subtotal = float(quote.get("subtotal", 0))
            vat = float(quote.get("vat", 0))
            total = float(quote.get("total", 0))

            items = quote.get("items", [])

            gross_profit = 0
            total_cost = 0
            template = ""

            for item in items:
                gross_profit += float(item.get("Profit", 0))
                total_cost += float(item.get("Line Cost", 0))

                if not template:
                    template = str(item.get("Template", ""))

            if subtotal > 0:
                gross_margin = (gross_profit / subtotal) * 100
            else:
                gross_margin = 0

            all_quotes.append({
                "Quote Number": quote_number,
                "Customer": customer,
                "Company": company,
                "Site": site,
                "Salesperson": salesperson,
                "Subtotal": subtotal,
                "VAT": vat,
                "Total": total,
                "Total Cost": total_cost,
                "Gross Profit": gross_profit,
                "Gross Margin %": gross_margin,
                "Template": template,
                "File": filename
            })

        except Exception as e:
            print(f"Report load error for {filename}: {e}")

    return pd.DataFrame(all_quotes)


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

st.dataframe(
    salesperson_summary,
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

st.dataframe(
    template_summary,
    use_container_width=True,
    hide_index=True
)


st.subheader("Quote Register Report")

st.dataframe(
    filtered_df,
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