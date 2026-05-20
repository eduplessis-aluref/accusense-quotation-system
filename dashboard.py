import streamlit as st
import datetime

st.set_page_config(
    page_title="AccuSense Dashboard",
    layout="wide"
)

st.markdown("""
<style>
.main {
    background-color: #f5f7fa;
}
.dashboard-title {
    font-size: 34px;
    font-weight: 700;
    color: #0B4F9C;
}
.dashboard-subtitle {
    font-size: 18px;
    color: #4A4A4A;
}
.card {
    padding: 25px;
    border-radius: 16px;
    background-color: white;
    box-shadow: 0px 2px 10px rgba(0,0,0,0.08);
    text-align: center;
}
.card-title {
    font-size: 20px;
    font-weight: 600;
    color: #0B4F9C;
}
.card-text {
    font-size: 14px;
    color: #555555;
}
</style>
""", unsafe_allow_html=True)

col_logo, col_title = st.columns([1, 4])

with col_logo:
    st.image("Logo.png", width=180)

with col_title:
    st.markdown("<div class='dashboard-title'>AccuSense Quotation System</div>", unsafe_allow_html=True)
    st.markdown("<div class='dashboard-subtitle'>Industrial Monitoring & Predictive Solutions</div>", unsafe_allow_html=True)
    st.write(datetime.datetime.now().strftime("%A, %d %B %Y"))

st.divider()

st.subheader("Quick Actions")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class='card'>
        <div class='card-title'>Create New Quote</div>
        <div class='card-text'>Start a new customer quotation</div>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/1_Create_Quote.py", label="Open Quote System", icon="📄")

with col2:
    st.markdown("""
    <div class='card'>
        <div class='card-title'>Load / Revise Quote</div>
        <div class='card-text'>Recall previous quotations and create revisions</div>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/1_Create_Quote.py", label="Open Revisions", icon="🔁")

with col3:
    st.markdown("""
    <div class='card'>
        <div class='card-title'>Quote Register</div>
        <div class='card-text'>View quote history in Google Sheets</div>
    </div>
    """, unsafe_allow_html=True)
    st.link_button(
        "Open Google Sheet",
        "https://docs.google.com/spreadsheets/"
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