import streamlit as st
from modules.google_sheets import client, SPREADSHEET_NAME


@st.cache_data(ttl=120)
def load_users():
    sheet = client.open(SPREADSHEET_NAME).worksheet("Users")
    return sheet.get_all_records()


def authenticate_user(email, password):
    users = load_users()

    email = str(email).strip().lower()
    password = str(password).strip()

    for user in users:
        user_email = str(user.get("Email", "")).strip().lower()
        user_password = str(user.get("Password", "")).strip()
        active = str(user.get("Active", "")).strip().lower()

        if user_email == email and user_password == password and active == "yes":
            return {
                "Email": user.get("Email", ""),
                "Name": user.get("Name", ""),
                "Role": user.get("Role", ""),
                "Phone": user.get("Phone", ""),
            }

    return None


def require_login():
    if st.session_state.get("authenticated", False):
        return st.session_state.get("current_user", {})

    st.title("AccuSense Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = authenticate_user(email, password)

        if user:
            st.session_state.authenticated = True
            st.session_state.current_user = user
            st.rerun()
        else:
            st.error("Invalid login or inactive user.")

    st.stop()


def logout_button():
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.current_user = {}
        st.rerun()