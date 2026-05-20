import streamlit as st
from modules.ui import render_header

st.set_page_config(
    page_title="AccuSense Dashboard",
    layout="wide"
)

QUOTE_PAGE = "./Create_Quote"

GOOGLE_SHEET_URL = "PASTE_YOUR_FULL_GOOGLE_SHEET_URL_HERE"

render_header()

st.markdown(
    """
    <style>
    .action-link {
        text-decoration: none !important;
    }

    .action-card {
        background: white;
        padding: 26px;
        border-radius: 16px;
        box-shadow: 0px 2px 10px rgba(0,0,0,0.08);
        text-align: center;
        min-height: 145px;
        border: 1px solid #E6EAF0;
        transition: 0.15s ease-in-out;
    }

    .action-card:hover {
        transform: translateY(-2px);
        box-shadow: 0px 4px 14px rgba(0,0,0,0.14);
        border-color: #0B4F9C;
    }

    .action-title {
        font-size: 20px;
        font-weight: 700;
        color: #0B4F9C;
        margin-bottom: 10px;
    }

    .action-text {
        font-size: 14px;
        color: #444444;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.subheader("Quick Actions")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        f"""
        <a class="action-link" href="{QUOTE_PAGE}">
            <div class="action-card">
                <div class="action-title">📄 Create New Quote</div>
                <div class="action-text">Start a new customer quotation</div>
            </div>
        </a>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        f"""
        <a class="action-link" href="{QUOTE_PAGE}">
            <div class="action-card">
                <div class="action-title">🔁 Load / Revise Quote</div>
                <div class="action-text">Recall previous quotations and create revisions</div>
            </div>
        </a>
        """,
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        f"""
        <a class="action-link" href="{GOOGLE_SHEET_URL}" target="_blank">
            <div class="action-card">
                <div class="action-title">📊 Quote Register</div>
                <div class="action-text">Open quote history in Google Sheets</div>
            </div>
        </a>
        """,
        unsafe_allow_html=True
    )

st.divider()

st.subheader("AccuSense Solutions")

col1, col2, col3 = st.columns(3)

with col1:
    st.info("🔥 Hot metal ladle monitoring")
    st.info("🌡️ Bearing temperature monitoring")

with col2:
    st.info("⛏️ Coal stockpile temperature & CO₂ monitoring")
    st.info("⚡ Wireless electricity consumption monitoring")

with col3:
    st.info("💧 Silo and reservoir level monitoring")
    st.info("📡 LoRaWAN industrial sensor networks")