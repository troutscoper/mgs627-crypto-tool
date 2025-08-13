import requests
import pandas as pd
from datetime import datetime
import dash
from dash import dcc, html, Input, Output
import plotly.express as px

# --- Constants for API and UI ---
API_URL_HISTORY = "https://api.coingecko.com/api/v3/coins/"

def fetch_crypto_data(coin_id, currency, days):
    url = f"{API_URL_HISTORY}{coin_id}/market_chart?vs_currency={currency}&days={days}"
    response_history = requests.get(url)
    data_history = response_history.json()
    df_history = pd.DataFrame(data_history['prices'], columns=['timestamp', 'price'])
    # Convert timestamp to a readable datetime format
    df_history['timestamp'] = df_history['timestamp'].apply(lambda ts: datetime.fromtimestamp(ts / 1000))
    return df_history

print(fetch_crypto_data('bitcoin', 'usd', 30))