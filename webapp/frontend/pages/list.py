import streamlit as st
from api import list_equities


def show_popular(token):
    st.title("Popular U.S. Stocks")
    st.caption("Fetched from TastyTrade APIs")
    if not token:
        st.warning("Please enter your Session Token in the sidebar.")
        return

    with st.spinner("Fetching data..."):
        data = list_equities(token)

    if data:
        st.dataframe(
            [
                {
                    "Symbol": d["symbol"],
                    "Description": d["description"],
                    "Exchange": d.get("listed_market", ""),
                    "Lendability": d.get("lendability", ""),
                    "ETF": d.get("is_etf"),
                    "Active": d.get("active"),
                }
                for d in data
            ],
            use_container_width=True,
        )
    else:
        st.info("No stocks found or bad session token.")
