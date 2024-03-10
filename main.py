from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import pandas_ta as ta
import requests

app = Dash(external_stylesheets = [dbc.themes.CYBORG])

def create_dropdown(option, id_value):
    return html.Div(
        [
            html.H4(" ".join(id_value.replace("-", " ").split(" ")[:-1]),
             style = {
            "padding":"0px 30px 0px 30px",
        }),
            dcc.Dropdown(option, id=id_value, value=option[0])
        ], style = {
            "padding":"0px 30px 0px 30px"
        }
    )

app.layout = html.Div([
    html.Div([create_dropdown(["btcusd","ethusd","xrpusd"], "coin-select"),
    create_dropdown(["60","3600","86400"], "timeframe-select"),
    create_dropdown(["20","50","100"], "numBars-select")], 
    style = {
        "display":"flex",
        "margin":"auto",
        "width":"800px",
        "justify-content":"space-around" 
    }),

    html.Div([dcc.RangeSlider(0, 20, 1, value=[0,20], id="range-slider")], id="range-slider-container",
    style = {
        "width":"800px",
        "margin":"auto",
        "padding-top":"30px"
    }),

    dcc.Graph(id="candles"),
    dcc.Graph(id="indicator"),
    dcc.Interval(id="interval", interval=60000),  # Adjusted interval to 10 seconds
])


@app.callback(
    Output("range-slider-container", "children"),
    Input("numBars-select", "value")
)
def update_range_slider(numBars):
    return dcc.RangeSlider(min=0, max=int(numBars), step = int(int(numBars)/20),
            value = [0, int(numBars)], id="range-slider")

@app.callback(
    Output("candles", "figure"),
    Output("indicator", "figure"),
    Input("interval", "n_intervals"),
    Input("coin-select", "value"),
    Input("timeframe-select", "value"),
    Input("numBars-select", "value"),
    Input("range-slider", "value")

)
def update_figure(n_intervals, coin_pair, timeframe, numBars, range_values):
    try:
        base_url = f"https://www.bitstamp.net/api/v2/ohlc/{coin_pair}"

        params = {
            "step": timeframe,
            "limit": int(numBars) + 14,
        }

        data = requests.get(base_url, params=params).json()["data"]["ohlc"]

        data = pd.DataFrame(data)
        data.timestamp =  pd.to_datetime(pd.to_numeric(data['timestamp'], errors='coerce'), unit='s')

        data["rsi"] = ta.rsi(data.close.astype(float))

        data = data.iloc[14:]

        data = data.iloc[range_values[0]:range_values[1]]

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

        candles.update_layout(xaxis_rangeslider_visible=False, height=400, template="plotly_dark")
        candles.update_layout(transition_duration=500)

        indicator = px.line(x=data.timestamp, y=data.rsi, height=300, template="plotly_dark")
        indicator.update_layout(transition_duration=500)


        return candles, indicator

    except Exception as e:
        print(f"Error updating figure: {str(e)}")
        return go.Figure(), go.Figure()

if __name__ == "__main__":
    app.run_server(debug=True)
