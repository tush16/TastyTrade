import streamlit as st
from api import search_equities

st.title("Search for a Stock")
st.caption("Search by company name or ticker (live from TastyTrade APIs)")

token = st.session_state.get("session_token", "")

if not token:
    st.warning("Please enter your Session Token in the sidebar.")
else:
    query = st.text_input("Enter symbol or company name:", "")
    if query:
        if st.button("Search"):
            with st.spinner("Searching..."):
                results = search_equities(token, query.strip())

            if results:
                st.dataframe(
                    [
                        {
                            "Symbol": d.get("symbol", ""),
                            "Description": d.get("description", ""),
                        }
                        for d in results
                    ],
                    use_container_width=True,
                )
            else:
                st.info("No stocks matched your search.")
