import streamlit as st
import pandas as pd
from api import get_option_chain_nested

st.title("Option Chains")
st.caption("Fetch nested equity options for a stock symbol")

token = st.session_state.get("session_token", "")

if not token:
    st.warning("Please enter your Session Token in the sidebar.")
else:
    # Input symbol
    symbol = st.text_input("Enter stock symbol (e.g., AAPL):", "").upper().strip()

    if st.button("Fetch Option Chain") and symbol:
        with st.spinner(f"Fetching option chain for {symbol}..."):
            data = get_option_chain_nested(token, symbol)

        # Handle API error
        if isinstance(data, dict) and "error" in data:
            st.error(data["error"])
        elif isinstance(data, list) and data:
            # Convert list of dicts to DataFrame for display
            df = pd.DataFrame(data)

            # Select relevant columns to show, adjust as needed
            show_columns = [
                "symbol",
                "underlying-symbol",
                "option-type",
                "strike-price",
                "expiration-date",
                "days-to-expiration",
                "exercise-style",
                "active",
            ]
            show_columns = [col for col in show_columns if col in df.columns]

            if df.empty:
                st.info("No option chain data found.")
            else:
                st.dataframe(df, use_container_width=True)
        else:
            st.info("No option chain data found for this symbol.")
