import datetime
import streamlit as st

st.set_page_config(
    page_title="AccuSense Dashboard",
    layout="wide"
)

QUOTE_PAGE = "./Create_Quote"

st.markdown(
    """
    <style>
    .big-title {
        font-size: 24px;
        font-weight: 700;
        color: #0B4F9C;
    }

    .sub-title {
        font-size: 14px;
        color: #555555;
    }

    .action-card {
        background: white;
        padding: 24px;
        border-radius: 16px;
        box-shadow: 0px 2px 10px rgba(0,0,0,0.08);
        text-align: center;
        min-height: 130px;
        margin-bottom: 12px;
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
    }
    </style>
    """,
    unsafe_allow_html=True
)

col_logo, col_title = st.columns([1, 4])

with col_logo:
    st.image("Logo.png", width=450)

with col_title:
    st.markdown(
        "<div class='big-title'>AccuSense Quotation System</div>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<div class='sub-title'>Industrial Monitoring & Predictive Solutions</div>",
        unsafe_allow_html=True
    )
    st.write(datetime.datetime.now().strftime("%A, %d %B %Y"))

st.divider()

st.subheader("Quick Actions")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        """
        <div class="action-card">
            <div class="action-title">Create New Quote</div>
            <div class="action-text">Start a new customer quotation</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.link_button(
        "📄 Open Quote System",
        QUOTE_PAGE,
        use_container_width=True
    )

with col2:
    st.markdown(
        """
        <div class="action-card">
            <div class="action-title">Load / Revise Quote</div>
            <div class="action-text">Recall previous quotations and create revisions</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.link_button(
        "🔁 Open Revisions",
        QUOTE_PAGE,
        use_container_width=True
    )

with col3:
    st.markdown(
        """
        <div class="action-card">
            <div class="action-title">Quote Register</div>
            <div class="action-text">View quote history in Google Sheets</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.link_button(
        "📊 Open Google Sheet",
        "https://docs.google.com/spreadsheets/d/16ch_vgWWpf_ZxD64aAWCMUd2TyPJhv-QcCai0m7l3pI/edit?gid=979178217#gid=979178217",
        use_container_width=True
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