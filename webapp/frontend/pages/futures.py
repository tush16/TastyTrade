import streamlit as st
import pandas as pd
from api import list_futures, get_future_detail


def display_nested_dict(d, indent=0):
    """Recursively display nested dicts and lists nicely."""
    for key, value in d.items():
        if isinstance(value, dict):
            st.markdown(f"{'&nbsp;' * indent * 4}**{key}:**")
            display_nested_dict(value, indent + 1)
        elif isinstance(value, list):
            st.markdown(f"{'&nbsp;' * indent * 4}**{key}:**")
            if len(value) == 0:
                st.write("No items.")
            elif all(isinstance(i, dict) for i in value):
                # Convert list of dicts to table
                df = pd.DataFrame(value)
                st.dataframe(df)
            else:
                # List of primitives
                st.write(", ".join(str(i) for i in value))
        else:
            st.markdown(f"{'&nbsp;' * indent * 4}**{key}:** {value}")


st.title("Futures Contracts")
st.caption("List of futures contracts fetched from backend")

token = st.session_state.get("session_token", "")

if not token:
    st.warning("Please enter your Session Token in the sidebar.")
else:
    with st.spinner("Fetching futures list..."):
        data = list_futures(token)

    if isinstance(data, dict) and "error" in data:
        st.error(data["error"])
    elif isinstance(data, list) and data:
        df = pd.DataFrame(data)
        df["display_symbol"] = df["symbol"].str.lstrip("/")
        show_columns = [
            "display_symbol",
            "active",
            "exchange",
            "expiration-date",
            "contract-size",
            "is-tradeable",
            "product-group",
        ]
        show_columns = [col for col in show_columns if col in df.columns]
        st.dataframe(
            df[show_columns].rename(columns={"display_symbol": "Symbol"}),
            use_container_width=True,
        )

        st.markdown("---")
        st.subheader("Get Details for a Specific Future")
        symbol_input = (
            st.text_input("Enter Future Symbol (e.g., GEZ5):").strip().upper()
        )

        if st.button("Fetch Future Details") and symbol_input:
            with st.spinner(f"Fetching details for {symbol_input}..."):
                detail = get_future_detail(token, symbol_input)

            if isinstance(detail, dict) and "error" in detail:
                st.error(detail["error"])
            elif detail:
                # Pretty display:

                st.markdown(f"## Details for {symbol_input}")

                # Basic fields at top
                basic_fields = [
                    "symbol",
                    "active",
                    "exchange",
                    "expiration-date",
                    "contract-size",
                    "is-tradeable",
                    "product-group",
                    "tick-size",
                    "last-trade-date",
                ]
                # Display basic fields in key:value pairs
                for field in basic_fields:
                    if field in detail:
                        st.markdown(
                            f"**{field.replace('-', ' ').title()}:** {detail[field]}"
                        )

                # Future product details inside an expander
                fp = detail.get("future-product")
                if fp:
                    with st.expander("Future Product Details", expanded=True):
                        display_nested_dict(fp)

                # Option tick sizes - as table
                option_tick_sizes = detail.get("option-tick-sizes")
                if option_tick_sizes:
                    with st.expander("Option Tick Sizes"):
                        st.dataframe(pd.DataFrame(option_tick_sizes))

                # Spread tick sizes - as table
                spread_tick_sizes = detail.get("spread-tick-sizes")
                if spread_tick_sizes:
                    with st.expander("Spread Tick Sizes"):
                        st.dataframe(pd.DataFrame(spread_tick_sizes))

                # Tick sizes - as table
                tick_sizes = detail.get("tick-sizes")
                if tick_sizes:
                    with st.expander("Tick Sizes"):
                        st.dataframe(pd.DataFrame(tick_sizes))
            else:
                st.info(f"No details found for symbol {symbol_input}.")
    else:
        st.info("No futures data found or bad session token.")
