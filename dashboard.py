import urllib.parse
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
    .card-link {
        text-decoration: none !important;
    }

    .action-card {
        background: white;
        padding: 24px;
        border-radius: 16px;
        box-shadow: 0px 2px 10px rgba(0,0,0,0.08);
        text-align: center;
        min-height: 145px;
        border: 1px solid #E6EAF0;
        margin-bottom: 18px;
        transition: 0.15s ease-in-out;
        cursor: pointer;
    }

    .action-card:hover {
        transform: translateY(-3px);
        box-shadow: 0px 5px 16px rgba(0,0,0,0.16);
        border-color: #0B4F9C;
        background-color: #F7FAFF;
    }

    .action-title {
        font-size: 19px;
        font-weight: 700;
        color: #0B4F9C;
        margin-bottom: 10px;
    }

    .action-text {
        font-size: 14px;
        color: #444444;
        line-height: 1.4;
    }

    .click-hint {
        margin-top: 14px;
        font-size: 13px;
        font-weight: 600;
        color: #6CB33F;
    }
    </style>
    """,
    unsafe_allow_html=True
)

def clickable_card(title, text, link, hint="Click to open"):
    st.markdown(
        f"""
        <a class="card-link" href="{link}">
            <div class="action-card">
                <div class="action-title">{title}</div>
                <div class="action-text">{text}</div>
                <div class="click-hint">{hint}</div>
            </div>
        </a>
        """,
        unsafe_allow_html=True
    )


st.subheader("Quick Actions")

col1, col2, col3 = st.columns(3)

with col1:
    clickable_card(
        "📄 Create New Quote",
        "Start a blank customer quotation.",
        QUOTE_PAGE,
        "Open Quote System"
    )

with col2:
    clickable_card(
        "🔁 Load / Revise Quote",
        "Recall previous quotations and create revisions.",
        QUOTE_PAGE,
        "Open Revisions"
    )

with col3:
    clickable_card(
        "📊 Quote Register",
        "Open quote history in Google Sheets.",
        GOOGLE_SHEET_URL,
        "Open Google Sheet"
    )

st.divider()

st.subheader("AccuSense Solution Templates")

solution_cards = [
    {
        "title": "⛽ Diesel Monitoring",
        "text": "Entry-level diesel tank monitoring solution.",
        "template": "Diesel Monitoring Entry Level",
    },
    {
        "title": "🔥 Hot Metal Ladle Monitoring",
        "text": "Early warning hot metal burn-through prevention.",
        "template": "Hot Metal Ladle Monitoring Entry Level",
    },
    {
        "title": "⛏️ Coal Stockpile Monitoring",
        "text": "Temperature and CO₂ monitoring for spontaneous combustion risk.",
        "template": "Coal Stockpile Monitoring Entry Level",
    },
    {
        "title": "🌡️ Bearing Temperature Monitoring",
        "text": "Wireless bearing temperature monitoring for downtime prevention.",
        "template": "Bearing Monitoring Entry Level",
    },
    {
        "title": "⚡ Energy Monitoring",
        "text": "Wireless electricity consumption monitoring.",
        "template": "Energy Monitoring Entry Level",
    },
    {
        "title": "💧 Reservoir / Silo Level",
        "text": "Wireless level monitoring for tanks, reservoirs and silos.",
        "template": "Reservoir Level Monitoring Entry Level",
    },
]

for row_start in range(0, len(solution_cards), 3):
    cols = st.columns(3)

    for idx, card in enumerate(solution_cards[row_start:row_start + 3]):
        template_encoded = urllib.parse.quote(card["template"])
        template_link = f"{QUOTE_PAGE}?template={template_encoded}"

        with cols[idx]:
            clickable_card(
                card["title"],
                card["text"],
                template_link,
                "Use Template"
            )