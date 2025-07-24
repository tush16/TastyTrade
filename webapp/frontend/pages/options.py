# pages/options.py

import streamlit as st
import pandas as pd
from api import get_equity_options

st.title("Equity Options Metadata")
st.caption("Fetch option data for U.S. stocks")

# Get session token from st.session_state (set in app.py sidebar)
token = st.session_state.get("session_token", "")

if not token:
    st.warning("Please enter your Session Token in the sidebar.")
else:
    # Input stock symbols comma separated
    stocks_input = st.text_input("Enter stock symbols (comma separated):", "AAPL,TSLA")
    stock_symbols = [s.strip().upper() for s in stocks_input.split(",") if s.strip()]

    # Option filters
    active = st.checkbox("Only Active Options", value=True)
    with_expired = st.checkbox("Include Expired Options", value=False)

    if st.button("Fetch Equity Options") and stock_symbols:
        with st.spinner("Fetching equity options..."):
            data = get_equity_options(
                token, stock_symbols, active=active, with_expired=with_expired
            )

        if data:
            # Handle API error response
            if isinstance(data, dict) and "error" in data:
                st.error(f"API Error: {data['error']}")
            else:
                # Convert to DataFrame and keep relevant columns
                df = pd.DataFrame(data)
                if not df.empty:
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
                    # Only display columns that exist in the data to avoid KeyError
                    show_columns_filtered = [
                        col for col in show_columns if col in df.columns
                    ]
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("No options data found.")
        else:
            st.error("Failed to fetch data or no data returned.")
