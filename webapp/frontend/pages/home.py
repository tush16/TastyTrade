import streamlit as st
import requests

API_BASE = "http://localhost:8000"


def login_user(login: str, password: str):
    url = f"{API_BASE}/session"
    payload = {"login": login, "password": password}
    try:
        resp = requests.post(url, json=payload, timeout=10)
        if resp.status_code == 200:
            return resp.json().get("session_token")
        elif resp.status_code == 401:
            st.error("Authentication failed: Invalid login or password.")
        else:
            st.error(f"Error: {resp.status_code} - {resp.text}")
    except Exception as e:
        st.error(f"Network or server error: {e}")
    return None


st.title("Welcome to the TastyTrade Analytical Dashboard")

token = st.session_state.get("session_token", "")

if not token:
    st.info("Please start your session by logging in.")

    with st.form("login_form", clear_on_submit=False):
        login = st.text_input("Email (login)", value="")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Start Session")

        if submitted:
            if not login or not password:
                st.warning("Please enter both login and password.")
            else:
                token = login_user(login, password)
                if token:
                    st.success("Login successful!")
                    st.session_state.session_token = token
                    st.rerun()
                else:
                    st.session_state.session_token = ""
else:
    st.success("Session started!")
    st.write("You can navigate using the sidebar.")

    if st.button("Logout"):
        st.session_state.session_token = ""
        st.rerun()
