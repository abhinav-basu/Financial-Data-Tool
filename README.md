# Financial-Data-Tool

A small Streamlit app for fetching historical stock market data from Indian and
US exchanges, powered by [Quandl (Nasdaq Data Link)](https://data.nasdaq.com/).

## Features

- Dropdown to pick a country (India / USA) and, within it, an exchange:
  - India: NSE, BSE
  - USA: NASDAQ, NYSE
- Ticker symbol input with example symbols per exchange
- Date range filter
- Price line chart, volume chart, data table, and CSV export

## Setup

```bash
pip install -r requirements.txt
```

Get a free API key at https://data.nasdaq.com/sign-up, then either:

- set it as an environment variable: `export QUANDL_API_KEY=your_key_here`, or
- paste it into the "Quandl / Nasdaq Data Link API key" field in the app sidebar

## Run

```bash
streamlit run app.py
```

## Notes on data coverage

- **NSE / BSE**: free end-of-day data for Indian equities.
- **NASDAQ / NYSE**: data comes from Nasdaq Data Link's `EOD` database, most of
  which requires a paid subscription. Symbols your API key doesn't have access
  to will return an error from Quandl explaining the restriction.

Ticker symbols are passed straight through to Quandl as `<DATABASE>/<TICKER>`
(e.g. `NSE/INFY`, `EOD/AAPL`), so any dataset code your API key can access will
work even if it isn't in the example list.
