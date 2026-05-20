import urllib.parse
import streamlit as st
from modules.ui import render_header
from modules.google_sheets import load_solution_templates

st.set_page_config(
    page_title="AccuSense Dashboard",
    layout="wide"
)

QUOTE_PAGE = "./Create_Quote"
GOOGLE_SHEET_URL = "PASTE_YOUR_FULL_GOOGLE_SHEET_URL_HERE"

render_header()


@st.cache_data(ttl=300)
def get_cached_templates():
    return load_solution_templates()


st.markdown("""
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
</style>
""", unsafe_allow_html=True)


st.subheader("Quick Actions")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="action-card">
        <div class="action-title">📄 Create Blank Quote</div>
        <div class="action-text">Start a new quotation without a template.</div>
    </div>
    """, unsafe_allow_html=True)

    st.link_button(
        "Open Blank Quote",
        QUOTE_PAGE,
        use_container_width=True
    )

with col2:
    st.markdown("""
    <div class="action-card">
        <div class="action-title">🔁 Load / Revise Quote</div>
        <div class="action-text">Recall previous quotations and create revisions.</div>
    </div>
    """, unsafe_allow_html=True)

    st.link_button(
        "Open Revisions",
        QUOTE_PAGE,
        use_container_width=True
    )

with col3:
    st.markdown("""
    <div class="action-card">
        <div class="action-title">📊 Quote Register</div>
        <div class="action-text">Open quote history in Google Sheets.</div>
    </div>
    """, unsafe_allow_html=True)

    st.link_button(
        "Open Quote Register",
        GOOGLE_SHEET_URL,
        use_container_width=True
    )

st.divider()

st.markdown("### AccuSense Solution Templates")
st.info("Select a solution below. The default products will load directly into the quote.")

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

        for idx, template_name in enumerate(template_names[row_start:row_start + cols_per_row]):

            with cols[idx]:

                template_encoded = urllib.parse.quote(template_name)
                quote_link = f"{QUOTE_PAGE}?template={template_encoded}"

                st.link_button(
                    template_name,
                    quote_link,
                    use_container_width=True
                )

else:
    st.warning("No solution templates found in Google Sheets.")