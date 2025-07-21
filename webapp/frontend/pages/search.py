import streamlit as st
from api import search_equities


def show_search(token):
    st.title("Search for a Stock")
    st.caption("Search by company name or ticker (live from TastyTrade APIs).")
    if not token:
        st.warning("Please enter your Session Token in the sidebar.")
        return

    query = st.text_input("Enter symbol or company name:", "")
    if st.button("Search", disabled=not query):
        with st.spinner("Searching..."):
            results = search_equities(token, query)
        if results:
            st.dataframe(
                [
                    {
                        "Symbol": d["symbol"],
                        "Description": d["description"],
                    }
                    for d in results
                ],
                use_container_width=True,
            )
        else:
            st.info("No stocks matched your search.")
