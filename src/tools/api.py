import os
from dotenv import load_dotenv
import pandas as pd
import requests
import hmac
import hashlib
import time

from data.cache import get_cache
from data.models import Price

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

BINANCE_API_KEY = os.getenv('BINANCE_API_KEY')
BINANCE_SECRET_KEY = os.getenv('BINANCE_SECRET_KEY')

# Global cache instance
_cache = get_cache()


def get_prices(ticker: str, start_date: str, end_date: str) -> list[Price]:
    """Fetch price data from Binance API or cache."""

    # Vérification du cache d'abord
    if cached_data := _cache.get_prices(ticker):
        filtered_data = [
            Price(**price)
            for price in cached_data
            if start_date <= price["time"][:10] <= end_date
        ]
        if filtered_data:
            return filtered_data

    url = "https://api.binance.com/api/v3/klines"

    headers = {"X-MBX-APIKEY": BINANCE_API_KEY}

    params = {
        "symbol": ticker.upper(),
        "interval": "1d",
        "startTime": int(pd.Timestamp(start_date).timestamp() * 1000),
        "endTime": int(pd.Timestamp(end_date).timestamp() * 1000),
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        raise Exception(f"Erreur API Binance : {response.status_code} - {response.text}")

    data = response.json()

    prices = [
        Price(
            open=float(candle[1]),
            high=float(candle[2]),
            low=float(candle[3]),
            close=float(candle[4]),
            volume=float(candle[5]),
            time=pd.to_datetime(candle[0], unit="ms").strftime("%Y-%m-%dT%H:%M:%SZ"),
        )
        for candle in data
    ]

    if not prices:
        return []

    # Mise en cache des résultats
    _cache.set_prices(ticker, [p.model_dump() for p in prices])
    return prices


def prices_to_df(prices: list[Price]) -> pd.DataFrame:
    df = pd.DataFrame([p.model_dump() for p in prices])
    df["Date"] = pd.to_datetime(df["time"])
    df.set_index("Date", inplace=True)
    numeric_cols = ["open", "close", "high", "low", "volume"]
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric)
    return df


def get_price_data(ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
    prices = get_prices(ticker, start_date, end_date)
    return prices_to_df(prices)
