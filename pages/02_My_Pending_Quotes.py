import pandas as pd
import streamlit as st

from modules.ui import render_header
from modules.auth import require_login, logout_button
import modules.google_sheets as gs


st.set_page_config(
    page_title="My Pending Quotes",
    layout="wide"
)

current_user = require_login()

render_header()

st.sidebar.success(
    f"Logged in as: {current_user.get('Name', '')}"
)

logout_button()

st.title("My Pending Quotes")

salesperson_email = str(
    current_user.get("Email", "")
).strip().lower()

try:

    approvals_df = gs.load_approval_requests()

except Exception as e:

    st.error(
        f"Could not load pending quotes: {e}"
    )

    st.stop()


if approvals_df.empty:

    st.info("No approval requests found.")
    st.stop()


my_pending_df = approvals_df[
    (
        approvals_df["Salesperson Email"]
        .astype(str)
        .str.lower()
        == salesperson_email
    )
    &
    (
        approvals_df["Status"]
        .astype(str)
        .str.lower()
        == "pending"
    )
]


if my_pending_df.empty:

    st.success(
        "You currently have no pending quotes."
    )

else:

    st.dataframe(
        my_pending_df,
        use_container_width=True,
        hide_index=True
    )