from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import pandas_ta as ta
import requests

app = Dash()

app.layout = html.Div([
    dcc.Dropdown(
        id="coin-select",
        options=[
            {"label": "Bitcoin (BTC)", "value": "btcusd"},
            {"label": "Ethereum (ETH)", "value": "ethusd"},
            {"label": "Ripple (XRP)", "value": "xrpusd"}
        ],
        value="btcusd"
    ),
    dcc.Graph(id="candles"),
    dcc.Graph(id="indicator"),
    dcc.Interval(id="interval", interval=1000),  # Adjusted interval to 10 seconds
])

@app.callback(
    Output("candles", "figure"),
    Output("indicator", "figure"),
    Input("interval", "n_intervals"),
    Input("coin-select", "value"),
)
def update_figure(n_intervals, coin_pair):
    try:
        base_url = f"https://www.bitstamp.net/api/v2/ohlc/{coin_pair}"

        params = {
            "step": "60",
            "limit": int("30") + 14,
        }

        data = requests.get(base_url, params=params).json()["data"]["ohlc"]

        data = pd.DataFrame(data)
        data.timestamp = pd.to_datetime(data.timestamp, unit="s")

        data["rsi"] = ta.rsi(data.close.astype(float))

        data = data.iloc[14:]

        candles = go.Figure(
            data=[
                go.Candlestick(
                    x=data.timestamp,
                    open=data.open,
                    high=data.high,
                    low=data.low,
                    close=data.close
                )
            ]
        )

        candles.update_layout(xaxis_rangeslider_visible=False, height=400)

        indicator = px.line(x=data.timestamp, y=data.rsi, height=300)

        return candles, indicator

    except Exception as e:
        print(f"Error updating figure: {str(e)}")
        return go.Figure(), go.Figure()

if __name__ == "__main__":
    app.run_server(debug=True)
