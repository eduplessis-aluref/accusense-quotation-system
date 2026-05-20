import datetime
import streamlit as st


def render_header():
    st.markdown(
        """
        <style>
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
        """,
        unsafe_allow_html=True
    )

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