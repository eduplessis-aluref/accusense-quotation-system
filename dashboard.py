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
    .action-card {
        background: white;
        padding: 22px;
        border-radius: 16px;
        box-shadow: 0px 2px 10px rgba(0,0,0,0.08);
        text-align: center;
        min-height: 120px;
        border: 1px solid #E6EAF0;
        margin-bottom: 8px;
    }

    .action-title {
        font-size: 18px;
        font-weight: 700;
        color: #0B4F9C;
        margin-bottom: 8px;
    }

    .action-text {
        font-size: 14px;
        color: #444444;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =====================================================
# QUICK ACTIONS
# =====================================================

st.subheader("Quick Actions")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        """
        <div class="action-card">
            <div class="action-title">📄 Create New Quote</div>
            <div class="action-text">Start a blank quotation</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button("Open Quote System", use_container_width=True):
        st.query_params["template"] = ""
        st.switch_page("pages/Create_Quote.py")

with col2:
    st.markdown(
        """
        <div class="action-card">
            <div class="action-title">🔁 Load / Revise Quote</div>
            <div class="action-text">Recall previous quotations and create revisions</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button("Open Revisions", use_container_width=True):
        st.switch_page("pages/Create_Quote.py")

with col3:
    st.markdown(
        """
        <div class="action-card">
            <div class="action-title">📊 Quote Register</div>
            <div class="action-text">Open quote history in Google Sheets</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.link_button(
        "Open Quote Register",
        GOOGLE_SHEET_URL,
        use_container_width=True
    )

st.divider()

# =====================================================
# SOLUTION TEMPLATE BUTTONS
# =====================================================

st.subheader("AccuSense Solution Templates")

solution_cards = [
    {
        "title": "⛽ Diesel Monitoring",
        "text": "Entry-level diesel tank monitoring solution",
        "template": "Diesel Monitoring Entry Level",
        "button": "Use Diesel Template"
    },
    {
        "title": "🔥 Hot Metal Ladle Monitoring",
        "text": "Early warning hot metal burn-through prevention",
        "template": "Hot Metal Ladle Monitoring Entry Level",
        "button": "Use Ladle Template"
    },
    {
        "title": "⛏️ Coal Stockpile Monitoring",
        "text": "Temperature and CO₂ monitoring for spontaneous combustion risk",
        "template": "Coal Stockpile Monitoring Entry Level",
        "button": "Use Coal Template"
    },
    {
        "title": "🌡️ Bearing Temperature Monitoring",
        "text": "Wireless bearing temperature monitoring for downtime prevention",
        "template": "Bearing Monitoring Entry Level",
        "button": "Use Bearing Template"
    },
    {
        "title": "⚡ Energy Monitoring",
        "text": "Wireless electricity consumption monitoring",
        "template": "Energy Monitoring Entry Level",
        "button": "Use Energy Template"
    },
    {
        "title": "💧 Reservoir / Silo Level",
        "text": "Wireless level monitoring for tanks, reservoirs and silos",
        "template": "Reservoir Level Monitoring Entry Level",
        "button": "Use Level Template"
    },
]

for row_start in range(0, len(solution_cards), 3):

    cols = st.columns(3)

    for idx, card in enumerate(
        solution_cards[row_start:row_start + 3]
    ):

        with cols[idx]:

            st.markdown(
                f"""
                <div class="action-card">
                    <div class="action-title">{card["title"]}</div>
                    <div class="action-text">{card["text"]}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

            if st.button(
                card["button"],
                key=f"template_{card['template']}",
                use_container_width=True
            ):
                st.query_params["template"] = card["template"]
                st.switch_page("pages/Create_Quote.py")