import urllib.parse
import streamlit as st
from modules.ui import render_header
from modules.google_sheets import load_

st.set_page_config(
    page_title="AccuSense Dashboard",
    layout="wide"
)

QUOTE_PAGE = "./Create_Quote"

GOOGLE_SHEET_URL = "PASTE_YOUR_FULL_GOOGLE_SHEET_URL_HERE"

render_header()

@st.cache_data(ttl=300)
def get_cached_templates():
    return load_()

# =====================================================
# DASHBOARD PAGE CSS
# =====================================================

st.markdown("""
<style>

/* Dashboard cards */
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

/* Dashboard card headings */
.action-title {
    font-size: 19px;
    font-weight: 700;
    color: #0B4F9C;
    margin-bottom: 10px;
}

/* Dashboard card text */
.action-text {
    font-size: 14px;
    color: #444444;
    line-height: 1.4;
}

/* Template section panel */
.template-panel {
    background: white;
    padding: 28px;
    border-radius: 18px;
    box-shadow: 0px 2px 12px rgba(0,0,0,0.08);

    border: 1px solid #E6EAF0;

    margin-top: 10px;
}

/* Template section title */
.template-title {
    font-size: 22px;
    font-weight: 700;
    color: #0B4F9C;
    margin-bottom: 8px;
}

/* Template section description */
.template-text {
    font-size: 14px;
    color: #444444;
    margin-bottom: 18px;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# QUICK ACTIONS
# =====================================================

st.subheader("Quick Actions")

col1, col2, col3 = st.columns(3)

with col1:

    st.markdown("""
    <div class="action-card">
        <div class="action-title">📄 Create Blank Quote</div>
        <div class="action-text">
            Start a new quotation without a template.
        </div>
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
        <div class="action-text">
            Recall previous quotations and create revisions.
        </div>
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
        <div class="action-text">
            Open quote history in Google Sheets.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.link_button(
        "Open Quote Register",
        GOOGLE_SHEET_URL,
        use_container_width=True
    )

st.divider()

# =====================================================
# SOLUTION TEMPLATE SECTION
# =====================================================

st.markdown("### AccuSense Solution Templates")
st.info(
    "Select a solution below. The default products will load directly into the quote."
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

    selected_solution_label = st.selectbox(
        "Select Solution Template",
        [""] + template_names
    )

    if selected_solution_label:

        template_encoded = urllib.parse.quote(
            selected_solution_label
        )

        quote_link = (
            f"{QUOTE_PAGE}?template={template_encoded}"
        )

        st.link_button(
            "Create Quote From Selected Template",
            quote_link,
            use_container_width=True
        )

    else:
        st.info(
            "Select a solution template to create a pre-loaded quote."
        )

else:
    st.warning(
        "No solution templates found in Google Sheets."
    )
}

selected_solution_label = st.selectbox(
    "Select Solution Template",
    [""] + list(.keys())
)

if selected_solution_label:

    selected_template = [
        selected_solution_label
    ]

    template_encoded = urllib.parse.quote(
        selected_template
    )

    quote_link = (
        f"{QUOTE_PAGE}?template={template_encoded}"
    )

    st.link_button(
        "Create Quote From Selected Template",
        quote_link,
        use_container_width=True
    )

else:

    st.info(
        "Select a solution template to create a pre-loaded quote."
    )