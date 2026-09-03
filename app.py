"""Streamlit app: fetch and chart stock market data from Quandl (Nasdaq Data Link)."""
import datetime as dt
import os

import plotly.graph_objects as go
import streamlit as st

from data_fetcher import EXCHANGES, QuandlFetchError, fetch_price_history

PRICE_COLOR = "#2a78d6"
VOLUME_COLOR = "#9ca3af"

st.set_page_config(page_title="Financial Data Tool", page_icon="📈", layout="wide")

st.title("📈 Financial Data Tool")
st.caption(
    "Fetch historical stock market data from Indian and US exchanges via "
    "Quandl (Nasdaq Data Link)."
)

with st.sidebar:
    st.header("Query")

    api_key = st.text_input(
        "Quandl / Nasdaq Data Link API key",
        value=os.environ.get("QUANDL_API_KEY", ""),
        type="password",
        help=(
            "Get a free key at data.nasdaq.com/sign-up. "
            "Defaults to the QUANDL_API_KEY environment variable if set."
        ),
    )

    country = st.selectbox("Country", ["India", "USA"])

    country_exchanges = {
        key: exch for key, exch in EXCHANGES.items() if exch.country == country
    }
    exchange_key = st.selectbox(
        "Exchange",
        options=list(country_exchanges.keys()),
        format_func=lambda k: country_exchanges[k].label,
    )
    exchange = country_exchanges[exchange_key]

    ticker = st.text_input(
        "Ticker symbol",
        value=exchange.example_tickers[0],
        help=f"Examples: {', '.join(exchange.example_tickers)}. {exchange.notes}",
    )

    today = dt.date.today()
    date_range = st.date_input(
        "Date range",
        value=(today - dt.timedelta(days=365), today),
        max_value=today,
    )
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date, end_date = date_range[0], today

    submitted = st.button("Fetch data", type="primary", use_container_width=True)

if submitted:
    if not api_key:
        st.error("Enter your Quandl / Nasdaq Data Link API key in the sidebar.")
    elif not ticker.strip():
        st.error("Enter a ticker symbol.")
    else:
        with st.spinner(f"Fetching {ticker.strip().upper()} from {exchange.label}..."):
            try:
                df = fetch_price_history(
                    exchange_key, ticker, start_date, end_date, api_key
                )
            except QuandlFetchError as exc:
                st.error(str(exc))
                df = None

        if df is not None:
            st.session_state["data"] = df
            st.session_state["meta"] = {
                "exchange_key": exchange_key,
                "exchange_label": exchange.label,
                "ticker": ticker.strip().upper(),
            }

if "data" in st.session_state:
    df = st.session_state["data"]
    meta = st.session_state["meta"]

    price_col = next(
        (c for c in ["Close", "Last", "Close Price", "Settle"] if c in df.columns),
        None,
    )
    volume_col = next((c for c in df.columns if "volume" in c.lower()), None)

    st.subheader(f"{meta['ticker']} — {meta['exchange_label']}")

    if price_col:
        col1, col2, col3 = st.columns(3)
        first, last = df[price_col].iloc[0], df[price_col].iloc[-1]
        col1.metric("Latest close", f"{last:,.2f}")
        col2.metric(
            "Change over period",
            f"{last - first:,.2f}",
            f"{(last / first - 1) * 100:,.2f}%" if first else None,
        )
        col3.metric("Trading days", len(df))

        fig = go.Figure(
            go.Scatter(
                x=df["Date"],
                y=df[price_col],
                mode="lines",
                line=dict(color=PRICE_COLOR, width=2),
                hovertemplate="%{x|%b %d, %Y}<br>%{y:,.2f}<extra></extra>",
            )
        )
        fig.update_layout(
            height=420,
            margin=dict(l=10, r=10, t=30, b=10),
            yaxis_title=price_col,
            hovermode="x unified",
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning(
            "No recognizable price column found; showing raw data returned by Quandl."
        )

    if volume_col:
        vol_fig = go.Figure(
            go.Bar(
                x=df["Date"],
                y=df[volume_col],
                marker_color=VOLUME_COLOR,
                hovertemplate="%{x|%b %d, %Y}<br>%{y:,.0f}<extra></extra>",
            )
        )
        vol_fig.update_layout(
            height=200,
            margin=dict(l=10, r=10, t=10, b=10),
            yaxis_title=volume_col,
            showlegend=False,
        )
        st.plotly_chart(vol_fig, use_container_width=True)

    st.dataframe(df, use_container_width=True, hide_index=True)

    st.download_button(
        "Download CSV",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name=f"{meta['ticker']}_{meta['exchange_key']}.csv",
        mime="text/csv",
    )
else:
    st.info(
        "Enter your API key, choose a country, exchange and ticker, pick a date "
        "range, then click **Fetch data**."
    )
