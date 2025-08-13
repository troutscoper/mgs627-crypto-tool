import requests
import pandas as pd
from datetime import datetime
import dash
from dash import dcc, html, Input, Output
import plotly.express as px

# --- Constants for API and UI ---
API_URL_HISTORY = "https://api.coingecko.com/api/v3/coins/"
API_URL_GLOBAL = "https://api.coingecko.com/api/v3/global"

CRYPTO_LIST = CRYPTO_LIST = {
    'bitcoin': 'Bitcoin (BTC)',
    'ethereum': 'Ethereum (ETH)',
    'tether': 'Tether (USDT)',
    'binancecoin': 'BinanceCoin (BNB)',
    'solana': 'Solana (SOL)',
    'ripple': 'Ripple (XRP)',
    'dogecoin': 'Dogecoin (DOGE)',
    'usd-coin': 'USD Coin (USDC)',
    'staked-ether': 'Lido Staked Ether (STETH)',
    'tron': 'Tron (TRX)'
}

CURRENCY_LIST = {
    'usd': 'USD ($)', 'eur': 'EUR (€)', 'jpy': 'JPY (¥)', 'gbp': 'GBP (£)', 'cad': 'CAD ($)'
}
DAYS_LIST = {
    'Last 1 day': 1,
    'Last 7 days': 7,
    'Last 30 days': 30,
    'Last 60 days': 60,
    'Last 90 days': 90
}


def fetch_crypto_data(coin_id, currency, days):
    """
    Fetches historical price data for a given cryptocurrency and currency
    over the last 'days' (1, 7, 30, 60, or 90) from the CoinGecko API.

    Args:
        coin_id (str): The ID of the cryptocurrency (e.g., 'bitcoin').
        currency (str): The currency to compare against (e.g., 'usd').

    Returns:
        pd.DataFrame: A DataFrame with 'timestamp' and 'price' columns, or an
                      empty DataFrame if the API call fails.
    """
    try:
        url = f"{API_URL_HISTORY}{coin_id}/market_chart?vs_currency={currency}&days={days}"
        response_history = requests.get(url)
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


def fetch_global_market_data():
    """
    Fetches current market share as a percentage for each cryptocurrency.

    Returns: pd.DataFrame: A DataFrame with 'coin' and 'percentage' columns
    """
    headers = {
        "accept": "application/json",
        "x-cg-demo-api-key": "CG-cCkes31SUqyJqWPRRQAExaMb"
    }
    try:
        response = requests.get(API_URL_GLOBAL, headers=headers)
        mdata = response.json()

        # Convert dict to DataFrame
        market_data = mdata["data"]["market_cap_percentage"]
        df_market = pd.DataFrame(list(market_data.items()), columns=['coin', 'percentage'])
        df_market['coin'] = df_market['coin'].str.capitalize()
        df_market = df_market.sort_values(by='percentage', ascending=False).head(10)
        return df_market
    except requests.exceptions.RequestException as e:
        print(f"Error fetching global market data: {e}")
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
                options=[
                    {'label': name, 'value': coin_id} for coin_id, name in CRYPTO_LIST.items()
                ],
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
                options=[
                    {'label': name, 'value': value} for value, name in CURRENCY_LIST.items()
                ],
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
        }),

        html.Div([
            html.H2("Select a Time Frame:", style={'fontSize': '24px', 'marginRight': '10px'}),
            dcc.Dropdown(
                id='days-dropdown',
                options=[
                    {'label': name, 'value': value} for name, value in DAYS_LIST.items()
                ],
                value=7,  # Default value
                clearable=False,
                style={'width': '300px', 'color': '#333', 'margin': 'auto'}
            ),
        ], style={
            'display': 'flex',
            'flexDirection': 'column',
            'justifyContent': 'center',
            'alignItems': 'center',
            'marginBottom': '20px'
        }),
    ], style={'display': 'flex', 'justifyContent': 'space-around', 'alignItems': 'center', 'flexWrap': 'wrap'}),

    dcc.Graph(
        id='price-graph',
        style={'height': '70vh', 'width': '90%', 'margin': 'auto', 'border': '1px solid #444', 'borderRadius': '10px'}),
    dcc.Graph(
        id='marketcap-graph',
        style={'height': '70vh', 'width': '90%', 'margin': 'auto', 'border': '1px solid #444', 'borderRadius': '10px'})
])


# --- Callback to update the graph ---
@app.callback(
    Output('price-graph', 'figure'),
    Input('crypto-dropdown', 'value'),
    Input('currency-dropdown', 'value'),
    Input('days-dropdown', 'value')
)
def update_graph(selected_coin, selected_currency, days):
    """
    Updates the price graph based on the selected cryptocurrency and currency.
    """
    df_history = fetch_crypto_data(selected_coin, selected_currency, days)

    # Check if the DataFrame is not empty
    if not df_history.empty:
        # Create the line plot using Plotly Express
        price_graph = px.line(data_frame=df_history,
                              x='timestamp',
                              y='price',
                              labels={'timestamp': 'Date', 'price': f"Price ({CURRENCY_LIST.get(selected_currency)})"}
                              )

        # Update the layout for better visual aesthetics
        price_graph.update_layout(
            title_text=f"{CRYPTO_LIST.get(selected_coin, selected_coin)} Price (Last 7 Days)",
            template="plotly_dark",
            plot_bgcolor='#2a2a2a',
            paper_bgcolor='#1a1a1a',
            font_color='#ffffff',
            hovermode="x unified"
        )
        return price_graph
    else:
        return px.line(pd.DataFrame(columns=['timestamp', 'price']))

# Callback for market dominance graph
@app.callback(
    Output('marketcap-graph', 'figure'),
    Input('crypto-dropdown', 'value')  # Or any input that should trigger update
)

def update_market_dominance(_):
    """
    Updates the price graph based on the selected cryptocurrency and currency.
    """
    df_dominance = fetch_global_market_data()
    if not df_dominance.empty:
        market_cap_graph = px.bar(df_dominance, x="coin", y="percentage",
                     title="Cryptocurrency Market Cap Dominance",
                     text="percentage")
        market_cap_graph.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
        market_cap_graph.update_layout(
            xaxis_title="Coin",
            yaxis_title="Percentage",
            template="plotly_dark",
            plot_bgcolor='#2a2a2a',
            paper_bgcolor='#1a1a1a',
            font_color='#ffffff',
            hovermode="closest"
        )
        return market_cap_graph
    else:
        return px.bar(pd.DataFrame(columns=['coin', 'percentage']))

# --- Run the App ---
if __name__ == '__main__':
    app.run(debug=True)

