import urllib.parse
import streamlit as st

from modules.ui import render_header
from modules.google_sheets import load_solution_templates
from modules.auth import require_login, logout_button

st.set_page_config(page_title="AccuSense Dashboard", layout="wide")

current_user = require_login()

from modules.auth import require_login, logout_button

QUOTE_PAGE = "./Create_Quote"
GOOGLE_SHEET_URL = "PASTE_YOUR_FULL_GOOGLE_SHEET_URL_HERE"

render_header()

st.sidebar.success(f"Logged in as: {current_user.get('Name', '')}")

logout_button()

st.sidebar.divider()

if st.sidebar.button("🔄 Refresh Google Sheets", use_container_width=True):
    st.cache_data.clear()
    st.sidebar.success("Google Sheet data refreshed")
    st.rerun()


@st.cache_data(ttl=300)
def get_cached_templates():
    return load_solution_templates()


st.markdown("""
<style>

.card-link {
    text-decoration: none !important;
}

.action-card {
    background: #EEF2F6;
    padding: 28px;
    border-radius: 16px;
    box-shadow: 0px 3px 12px rgba(0,0,0,0.12);
    text-align: center;
    min-height: 145px;
    border: 1px solid #D6DEE8;
    margin-bottom: 18px;
    transition: 0.15s ease-in-out;
    cursor: pointer;
}

.action-card:hover {
    background: #E3E9F0;
    border-color: #0B4F9C;
    transform: translateY(-2px);
    box-shadow: 0px 5px 16px rgba(0,0,0,0.16);
}

.action-title {
    font-size: 19px;
    font-weight: 800;
    color: #0B4F9C;
    margin-bottom: 10px;
}

.action-text {
    font-size: 14px;
    color: #444444;
    line-height: 1.4;
}

.click-hint {
    margin-top: 16px;
    font-size: 13px;
    font-weight: 800;
    color: #0B4F9C;
}

</style>
""", unsafe_allow_html=True)


def clickable_card(title, text, link, hint):
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
        "📄 Create Blank Quote",
        "Start a new quotation without a template.",
        QUOTE_PAGE,
        "Open Blank Quote"
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
        "Open Quote Register"
    )

st.divider()

st.markdown("### AccuSense Solution Templates")
st.info(
    "Create a quote from a pre-defined solution template below."
)

templates_df = get_cached_templates()

if not templates_df.empty:

    template_names = sorted(
        templates_df["Template Name"]
        .dropna()
        .astype(str)
        .str.strip()
        .unique()
    )

    cols_per_row = 3

    for row_start in range(0, len(template_names), cols_per_row):

        cols = st.columns(cols_per_row)

        for idx, template_name in enumerate(
            template_names[row_start:row_start + cols_per_row]
        ):

            with cols[idx]:

                template_encoded = urllib.parse.quote(template_name)

                quote_link = (
                    f"{QUOTE_PAGE}?template={template_encoded}"
                )

            clickable_card(
                template_name,
                "Create quote from this solution template.",
                quote_link,
                "Use Template"
)

else:
    st.warning("No solution templates found in Google Sheets.")