import streamlit as st

from modules.ui import render_header
from modules.google_sheets import load_solution_templates
from modules.auth import require_login, logout_button

st.set_page_config(page_title="AccuSense Dashboard", layout="wide")

current_user = {
    "Name": "Testing User",
    "Email": "",
    "Phone": "",
    "Role": "Admin"

GOOGLE_SHEET_URL = "PASTE_YOUR_FULL_GOOGLE_SHEET_URL_HERE"

render_header()

st.sidebar.success(f"Logged in as: {current_user.get('Name', '')}")

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
.action-card {
    background: #EEF2F6;
    padding: 28px;
    border-radius: 16px;
    box-shadow: 0px 3px 12px rgba(0,0,0,0.12);
    text-align: center;
    min-height: 145px;
    border: 1px solid #D6DEE8;
    margin-bottom: 10px;
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


def dashboard_card(title, text):
    st.markdown(
        f"""
        <div class="action-card">
            <div class="action-title">{title}</div>
            <div class="action-text">{text}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


st.subheader("Quick Actions")

col1, col2, col3 = st.columns(3)

with col1:
    dashboard_card(
        "📄 Create Blank Quote",
        "Start a new quotation without a template."
    )

    if st.button("Open Blank Quote", key="open_blank_quote", use_container_width=True):
        st.session_state.selected_template_from_dashboard = ""
        st.switch_page("pages/Create_Quote.py")

with col2:
    dashboard_card(
        "🔁 Load / Revise Quote",
        "Recall previous quotations and create revisions."
    )

    if st.button("Open Revisions", key="open_revisions", use_container_width=True):
        st.session_state.selected_template_from_dashboard = ""
        st.switch_page("pages/Create_Quote.py")

with col3:
    dashboard_card(
        "📊 Quote Register",
        "Open quote history in Google Sheets."
    )

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

        for idx, template_name in enumerate(
            template_names[row_start:row_start + cols_per_row]
        ):

            with cols[idx]:

                dashboard_card(
                    template_name,
                    "Create quote from this solution template."
                )

                if st.button(
                    "Use Template",
                    key=f"template_{template_name}",
                    use_container_width=True
                ):
                    st.session_state.selected_template_from_dashboard = template_name
                    st.switch_page("pages/Create_Quote.py")

else:
    st.warning("No solution templates found in Google Sheets.")