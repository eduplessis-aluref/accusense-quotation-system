import datetime
import streamlit as st


def render_header():

    st.markdown("""
    <style>

    /* Sidebar background */
    section[data-testid="stSidebar"] {
        background-color: #F5F7FA;
    }

    /* Sidebar navigation area */
    [data-testid="stSidebarNav"] {
        padding-top: 18px;
    }

    /* Sidebar page buttons */
    [data-testid="stSidebarNav"] a {
        background: #F2F4F7 !important;

        border: 2px solid #D9E2EC !important;
        border-radius: 14px !important;

        margin-bottom: 14px !important;
        padding: 18px 18px !important;

        font-size: 24px !important;
        font-weight: 900 !important;

        color: #0B4F9C !important;

        box-shadow: 0px 2px 8px rgba(0,0,0,0.08);

        transition: 0.15s ease-in-out;

        text-decoration: none !important;
    }

    /* Hover effect */
    [data-testid="stSidebarNav"] a:hover {
        background: #E9EEF5 !important;
        border-color: #0B4F9C !important;
    }

    /* ACTIVE PAGE */
    [data-testid="stSidebarNav"] a[aria-current="page"] {
        background: #E3E8EF !important;

        color: #0B4F9C !important;

        border-color: #C7D0DC !important;
    }

    .accu-title {
        font-size: 24px;
        font-weight: 700;
        color: #0B4F9C;
        margin-top: 8px;
    }

    .accu-subtitle {
        font-size: 14px;
        color: #555555;
        margin-bottom: 4px;
    }

    .accu-date {
        font-size: 13px;
        color: #777777;
    }

    </style>
    """, unsafe_allow_html=True)

    st.image("Logo.png", width=420)

    st.markdown(
        "<div class='accu-title'>AccuSense Quotation System</div>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<div class='accu-subtitle'>Industrial Monitoring & Predictive Solutions</div>",
        unsafe_allow_html=True
    )

    st.markdown(
        f"<div class='accu-date'>{datetime.datetime.now().strftime('%A, %d %B %Y')}</div>",
        unsafe_allow_html=True
    )

    st.divider()