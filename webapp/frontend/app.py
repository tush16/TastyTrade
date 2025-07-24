import streamlit as st

if "session_token" not in st.session_state:
    st.session_state.session_token = ""

pages = [
    st.Page("pages/home.py", title="Home"),
    st.Page("pages/list.py", title="Popular Stocks"),
    st.Page("pages/options.py", title="Equity Options"),
    st.Page("pages/search.py", title="Search Stocks"),
    st.Page("pages/option_chain.py", title="Option Chain Nested"),
    st.Page("pages/futures.py", title="Futures"),
]

nav = st.navigation(pages, position="sidebar", expanded=True)
nav.run()
