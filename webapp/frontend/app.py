import streamlit as st
from pages.list import show_popular
from pages.search import show_search

st.set_page_config(page_title="Equities Dashboard", layout="wide")
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Popular Stocks", "Search Stocks"])

token = st.sidebar.text_input("Session Token 🔑", type="password")

if page == "Popular Stocks":
    show_popular(token)
elif page == "Search Stocks":
    show_search(token)
