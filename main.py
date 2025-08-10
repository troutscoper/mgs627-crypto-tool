import requests
import pandas as pd
from datetime import datetime
import dash
from dash import dcc, html, Input, Output
import plotly.express as px

# --- Constants for API and UI ---
API_URL_HISTORY = "https://api.coingecko.com/api/v3/coins/"
CRYPTO_LIST = {
    'bitcoin': 'Bitcoin (BTC)',
    'ethereum': 'Ethereum (ETH)',
    'tether': 'Tether (USDT)',
    'binancecoin': 'BinanceCoin (BNB)',
    'solana': 'Solana (SOL)',
    'ripple': 'Ripple (XRP)',
    'cardano': 'Cardano (ADA)',
    'dogecoin': 'Dogecoin (DOGE)',
    'shiba-inu': 'Shiba-Inu (SHIB)',
    'polkadot': 'Polkadot (DOT)'
}
CURRENCY_LIST = {
    'usd': 'USD ($)', 'eur': 'EUR (€)', 'jpy': 'JPY (¥)', 'gbp': 'GBP (£)', 'cad': 'CAD ($)'
}


def fetch_crypto_data(coin_id, currency):
    """
    Fetches historical price data for a given cryptocurrency and currency
    over the last 7 days from the CoinGecko API.

    Args:
        coin_id (str): The ID of the cryptocurrency (e.g., 'bitcoin').
        currency (str): The currency to compare against (e.g., 'usd').

    Returns:
        pd.DataFrame: A DataFrame with 'timestamp' and 'price' columns, or an
                      empty DataFrame if the API call fails.
    """
    try:
        url = f"{API_URL_HISTORY}{coin_id}/market_chart?vs_currency={currency}&days=7"
        response_history = requests.get(url)
        response_history.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        data_history = response_history.json()

        # Check if the 'prices' key exists in the response
        if 'prices' in data_history and data_history['prices']:
            df_history = pd.DataFrame(data_history['prices'], columns=['timestamp', 'price'])
            # Convert timestamp to a readable datetime format
            df_history['timestamp'] = df_history['timestamp'].apply(lambda ts: datetime.fromtimestamp(ts / 1000))
            return df_history
        else:
            return pd.DataFrame()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for {coin_id}: {e}")
        return pd.DataFrame()


# --- Initialize the Dash App ---
app = dash.Dash(__name__)

# --- App Layout ---
app.layout = html.Div(style={
    'backgroundColor': '#1a1a1a',
    'color': '#ffffff',
    'fontFamily': 'Inter, sans-serif',
    'padding': '20px',
    'textAlign': 'center',
    'minHeight': '100vh'
}, children=[
    html.H1("Cryptocurrency Price Tracker", style={'fontSize': '48px', 'marginBottom': '20px', 'fontWeight': 'bold'}),

    html.Div([
        html.Div([
            html.H2("Select a Cryptocurrency:", style={'fontSize': '24px', 'marginRight': '10px'}),
            dcc.Dropdown(
                id='crypto-dropdown',
                options=[{'label': name, 'value': coin_id} for coin_id, name in CRYPTO_LIST.items()],
                value='bitcoin',  # Default value
                style={
                    'width': '300px',
                    'color': '#333',
                    'margin': 'auto'
                }
            ),
        ], style={
            'display': 'flex',
            'flexDirection': 'column',
            'justifyContent': 'center',
            'alignItems': 'center',
            'marginBottom': '20px'
        }),

        html.Div([
            html.H2("Select a Currency:", style={'fontSize': '24px', 'marginRight': '10px'}),
            dcc.Dropdown(
                id='currency-dropdown',
                options=[{'label': name, 'value': value} for value, name in CURRENCY_LIST.items()],
                value='usd',  # Default value
                style={
                    'width': '300px',
                    'color': '#333',
                    'margin': 'auto'
                }
            ),
        ], style={
            'display': 'flex',
            'flexDirection': 'column',
            'justifyContent': 'center',
            'alignItems': 'center',
            'marginBottom': '20px'
        })
    ], style={'display': 'flex', 'justifyContent': 'space-around', 'alignItems': 'center', 'flexWrap': 'wrap'}),

    dcc.Graph(
        id='price-graph',
        style={'height': '70vh', 'width': '90%', 'margin': 'auto', 'border': '1px solid #444', 'borderRadius': '10px'}
    )
])


# --- Callback to update the graph ---
@app.callback(
    Output('price-graph', 'figure'),
    Input('crypto-dropdown', 'value'),
    Input('currency-dropdown', 'value')
)
def update_graph(selected_coin_id, selected_currency):
    """
    Updates the price graph based on the selected cryptocurrency and currency.
    """
    df_history = fetch_crypto_data(selected_coin_id, selected_currency)

    # Check if the DataFrame is not empty
    if not df_history.empty:
        # Create the line plot using Plotly Express
        price_graph = px.line(data_frame=df_history,
                              x='timestamp',
                              y='price',
                              labels={'timestamp': 'Date', 'price': f"Price ({CURRENCY_LIST[selected_currency]})"}
                              )

        # Update the layout for better visual aesthetics
        price_graph.update_layout(
            title_text=f"{CRYPTO_LIST.get(selected_coin_id, selected_coin_id)} Price (Last 7 Days)",
            title_x=0.5,
            template="plotly_dark",
            plot_bgcolor='#2a2a2a',
            paper_bgcolor='#1a1a1a',
            font_color='#ffffff',
            yaxis=dict(rangemode="tozero"),
            hovermode="x unified"
        )
        return price_graph
    else:
        # If no data is available, create an empty figure and add a message to the title
        empty_df = pd.DataFrame(columns=['timestamp', 'price'])
        empty_fig = px.line(empty_df)
        empty_fig.update_layout(
            title_text="No data available for this cryptocurrency.",
            title_x=0.5,
            template="plotly_dark",
            plot_bgcolor='#2a2a2a',
            paper_bgcolor='#1a1a1a',
            font_color='#ffffff'
        )
        return empty_fig


# --- Run the App ---
if __name__ == '__main__':
    app.run(debug=True)

