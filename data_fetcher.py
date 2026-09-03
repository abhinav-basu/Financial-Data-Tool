"""Fetch historical stock price data from Quandl (Nasdaq Data Link)."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass

import pandas as pd
import quandl


@dataclass(frozen=True)
class Exchange:
    label: str
    country: str
    database_code: str
    example_tickers: tuple[str, ...]
    notes: str


EXCHANGES: dict[str, Exchange] = {
    "NSE": Exchange(
        label="National Stock Exchange (NSE)",
        country="India",
        database_code="NSE",
        example_tickers=("SBIN", "INFY", "TCS", "RELIANCE", "HDFCBANK"),
        notes="Free end-of-day data for NSE-listed equities.",
    ),
    "BSE": Exchange(
        label="Bombay Stock Exchange (BSE)",
        country="India",
        database_code="BSE",
        example_tickers=("BOM500325", "BOM500180", "BOM532540"),
        notes="BSE tickers use the numeric scrip code prefixed with 'BOM'.",
    ),
    "NASDAQ": Exchange(
        label="NASDAQ",
        country="USA",
        database_code="EOD",
        example_tickers=("AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"),
        notes=(
            "Uses Nasdaq Data Link's EOD US Stock Prices database "
            "(most tickers need a paid subscription)."
        ),
    ),
    "NYSE": Exchange(
        label="New York Stock Exchange (NYSE)",
        country="USA",
        database_code="EOD",
        example_tickers=("JPM", "KO", "DIS", "IBM", "GE"),
        notes=(
            "Uses Nasdaq Data Link's EOD US Stock Prices database "
            "(most tickers need a paid subscription)."
        ),
    ),
}


class QuandlFetchError(RuntimeError):
    """Raised when Quandl data cannot be fetched."""


def fetch_price_history(
    exchange_key: str,
    ticker: str,
    start_date: dt.date,
    end_date: dt.date,
    api_key: str,
) -> pd.DataFrame:
    """Return a DataFrame of historical data for a ticker on the given exchange."""
    if not api_key:
        raise QuandlFetchError("A Quandl / Nasdaq Data Link API key is required.")
    if exchange_key not in EXCHANGES:
        raise QuandlFetchError(f"Unknown exchange '{exchange_key}'.")
    if start_date > end_date:
        raise QuandlFetchError("Start date must be before end date.")

    exchange = EXCHANGES[exchange_key]
    dataset_code = f"{exchange.database_code}/{ticker.strip().upper()}"

    quandl.ApiConfig.api_key = api_key
    try:
        df = quandl.get(dataset_code, start_date=start_date, end_date=end_date)
    except Exception as exc:  # quandl raises its own broad exception hierarchy
        raise QuandlFetchError(
            f"Could not fetch '{dataset_code}' from Quandl: {exc}"
        ) from exc

    if df.empty:
        raise QuandlFetchError(
            f"No data returned for '{dataset_code}' in the given date range."
        )

    df.index.name = "Date"
    return df.reset_index()
