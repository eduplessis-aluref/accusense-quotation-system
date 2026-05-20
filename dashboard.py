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
    .action-card {
        background: white;
        padding: 24px;
        border-radius: 16px;
        box-shadow: 0px 2px 10px rgba(0,0,0,0.08);
        text-align: center;
        min-height: 145px;
        border: 1px solid #E6EAF0;
        margin-bottom: 18px;
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

    .template-panel {
        background: white;
        padding: 28px;
        border-radius: 18px;
        box-shadow: 0px 2px 12px rgba(0,0,0,0.08);
        border: 1px solid #E6EAF0;
        margin-top: 10px;
    }

    .template-title {
        font-size: 22px;
        font-weight: 700;
        color: #0B4F9C;
        margin-bottom: 8px;
    }

    .template-text {
        font-size: 14px;
        color: #444444;
        margin-bottom: 18px;
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
            <div class="action-title">📄 Create Blank Quote</div>
            <div class="action-text">Start a new quotation without a template.</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.link_button(
        "Open Blank Quote",
        QUOTE_PAGE,
        use_container_width=True
    )

with col2:
    st.markdown(
        """
        <div class="action-card">
            <div class="action-title">🔁 Load / Revise Quote</div>
            <div class="action-text">Recall previous quotations and create revisions.</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.link_button(
        "Open Revisions",
        QUOTE_PAGE,
        use_container_width=True
    )

with col3:
    st.markdown(
        """
        <div class="action-card">
            <div class="action-title">📊 Quote Register</div>
            <div class="action-text">Open quote history in Google Sheets.</div>
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
# SOLUTION TEMPLATE SELECTOR
# =====================================================

st.markdown(
    """
    <div class="template-panel">
        <div class="template-title">AccuSense Solution Templates</div>
        <div class="template-text">
        Select a solution below. The default products will load directly into the quote.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

solution_templates = {
    "Diesel Monitoring - Entry Level": "Diesel Monitoring Entry Level",
    "Hot Metal Ladle Monitoring - Entry Level": "Hot Metal Ladle Monitoring Entry Level",
    "Coal Stockpile Monitoring - Entry Level": "Coal Stockpile Monitoring Entry Level",
    "Bearing Temperature Monitoring - Entry Level": "Bearing Monitoring Entry Level",
    "Energy Monitoring - Entry Level": "Energy Monitoring Entry Level",
    "Reservoir / Silo Level Monitoring - Entry Level": "Reservoir Level Monitoring Entry Level",
}

selected_solution_label = st.selectbox(
    "Select Solution Template",
    [""] + list(solution_templates.keys())
)

if selected_solution_label:
    selected_template = solution_templates[selected_solution_label]

    template_encoded = urllib.parse.quote(selected_template)
    quote_link = f"{QUOTE_PAGE}?template={template_encoded}"

    st.link_button(
        "Create Quote From Selected Template",
        quote_link,
        use_container_width=True
    )
else:
    st.info("Select a solution template to create a pre-loaded quote.")