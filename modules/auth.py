import streamlit as st
import modules.google_sheets as gs


def require_login():
    if "user" not in st.session_state:
        st.session_state.user = None

    if st.session_state.user is not None:
        return st.session_state.user

    st.title("Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        users_df = gs.load_users()

        users_df.columns = users_df.columns.astype(str).str.strip()

        users_df["Email"] = (
            users_df["Email"]
            .fillna("")
            .astype(str)
            .str.strip()
            .str.lower()
        )

        users_df["Password"] = (
            users_df["Password"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        matched_user = users_df[
            (users_df["Email"] == email.strip().lower())
            &
            (users_df["Password"] == password.strip())
        ]

        if matched_user.empty:
            st.error("Invalid email or password")
            st.stop()

        user_row = matched_user.iloc[0].to_dict()

        # Keep FULL user row, including Approval Limit and Can Approve
        st.session_state.user = user_row

        st.rerun()

    st.stop()


def logout_button():
    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.rerun()