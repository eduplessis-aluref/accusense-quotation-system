import streamlit as st
import pandas as pd
import modules.google_sheets as gs

st.write("Google Sheets module file:", gs.__file__)
st.write(
    "Has load_approval_requests:",
    hasattr(gs, "load_approval_requests")
)

from modules.ui import render_header
from modules.auth import require_login, logout_button
import modules.google_sheets as gs


st.set_page_config(
    page_title="Approvals",
    layout="wide"
)

current_user = require_login()

render_header()

st.sidebar.success(f"Logged in as: {current_user.get('Name', '')}")
logout_button()

st.title("Quote Approvals")

can_approve = (
    str(current_user.get("Can Approve", "No"))
    .strip()
    .lower()
    == "yes"
)

if not can_approve:
    st.error("You are not authorised to approve quotes.")
    st.stop()


try:
    approvals_df = gs.load_approval_requests()

except Exception as e:
    st.error(f"Could not load approval requests: {e}")
    st.stop()


if approvals_df.empty:
    st.info("No approval requests found.")
    st.stop()


approvals_df = approvals_df.reset_index()
approvals_df["Sheet Row"] = approvals_df["index"] + 2

pending_df = approvals_df[
    approvals_df["Status"].astype(str).str.lower() == "pending"
].copy()

st.subheader("Pending Approval Requests")

if pending_df.empty:
    st.success("No pending approvals.")
    st.stop()


for _, row in pending_df.iterrows():

    with st.container(border=True):

        st.write(f"### Quote: {row.get('Quote Number', '')}")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.write(f"**Customer:** {row.get('Customer', '')}")
            st.write(f"**Company:** {row.get('Company', '')}")

        with col2:
            st.write(f"**Salesperson:** {row.get('Salesperson', '')}")
            st.write(f"**Email:** {row.get('Salesperson Email', '')}")

        with col3:
            st.write(f"**Quote Total:** R {float(row.get('Quote Total', 0)):,.2f}")
            st.write(f"**Approval Limit:** R {float(row.get('Approval Limit', 0)):,.2f}")

        notes = st.text_area(
            "Approval Notes",
            key=f"notes_{row['Sheet Row']}"
        )

        approve_col, reject_col = st.columns(2)

        with approve_col:

            if st.button(
                "Approve",
                key=f"approve_{row['Sheet Row']}"
            ):

                gs.update_approval_status(
                    row_number=int(row["Sheet Row"]),
                    status="Approved",
                    approved_by=current_user.get("Name", ""),
                    notes=notes
                )

                st.success("Quote approved.")
                st.rerun()

        with reject_col:

            if st.button(
                "Reject",
                key=f"reject_{row['Sheet Row']}"
            ):

                gs.update_approval_status(
                    row_number=int(row["Sheet Row"]),
                    status="Rejected",
                    approved_by=current_user.get("Name", ""),
                    notes=notes
                )

                st.error("Quote rejected.")
                st.rerun()