import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output
import plotly.express as px
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dal import DataAccessLayer  # Ensure this DAL module is implemented
import pandas as pd


# Database setup
engine = create_engine("sqlite:///generation.db")
Session = sessionmaker(bind=engine)

# Choose a Bootswatch theme
BOOTSTRAP_THEME = dbc.themes.FLATLY  # or any other theme: CYBORG, LUX, etc.

app = dash.Dash(__name__, external_stylesheets=[BOOTSTRAP_THEME])


# Define a function to fetch data from the database
def fetch_data(dal_method):
    session = Session()
    dal = DataAccessLayer(session)
    data = getattr(dal, dal_method)()
    session.close()
    return data


# Define the layout of the application, including explanatory text
app.layout = html.Div(
    className="container",
    children=[
        html.H1("Energy Generation Dashboard", className="header-title"),
        html.Div(
            className="text-box",
            children=[
                dcc.Markdown(
                    """
                    ## Carbon Intensity Over Time
                    This graph shows the carbon intensity of electricity generation over time. 
                    Lower carbon intensity indicates a cleaner energy mix.
                """
                )
            ],
        ),
        dcc.Graph(id="carbon-intensity-graph"),
        html.Div(
            className="text-box",
            children=[
                dcc.Markdown(
                    """
                    ## Demand vs Generation Over Time
                    This graph compares the total electricity demand with the total generation over time.
                    It highlights the balance between energy consumption and production.
                """
                )
            ],
        ),
        dcc.Graph(id="demand-generation-graph"),
        html.Div(
            className="text-box",
            children=[
                dcc.Markdown(
                    """
                    ## Energy Mix
                    This pie chart displays the proportion of different energy types contributing to the total generation.
                    A diverse energy mix can be more resilient and sustainable.
                """
                )
            ],
        ),
        dcc.Graph(id="energy-mix-pie-chart"),
        html.Div(
            className="text-box",
            children=[
                dcc.Markdown(
                    """
                    ## Demand Breakdown
                    The bar chart shows the breakdown of electricity demand over time, 
                    including net demand, gross demand, and various other metrics.
                """
                )
            ],
        ),
        dcc.Graph(id="demand-breakdown-bar-chart"),
        # Interval component to trigger callbacks
        dcc.Interval(id="interval-component", interval=60000, n_intervals=0),
    ],
)


@app.callback(
    Output("carbon-intensity-graph", "figure"),
    [Input("interval-component", "n_intervals")],
)
def update_carbon_intensity_graph(n_intervals):
    data = fetch_data("get_carbon_intensity_over_time")
    df = pd.DataFrame(data, columns=["Time", "Carbon Intensity"])
    figure = px.line(
        df, x="Time", y="Carbon Intensity", title="Carbon Intensity Over Time"
    )
    return figure


@app.callback(
    Output("demand-generation-graph", "figure"),
    [Input("interval-component", "n_intervals")],
)
def update_demand_generation_graph(n_intervals):
    data = fetch_data("get_total_demand_and_generation_over_time")
    df = pd.DataFrame(data, columns=["Time", "Total Demand", "Total Generation"])
    figure = px.line(
        df,
        x="Time",
        y=["Total Demand", "Total Generation"],
        title="Demand vs Generation Over Time",
    )
    return figure


@app.callback(
    Output("energy-mix-pie-chart", "figure"),
    [Input("interval-component", "n_intervals")],
)
def update_energy_mix_pie_chart(n_intervals):
    data = fetch_data("get_energy_mix")
    df = pd.DataFrame(data, columns=["Energy Type", "Total Generation"])
    figure = px.pie(
        df, names="Energy Type", values="Total Generation", title="Energy Mix"
    )
    return figure


@app.callback(
    Output("demand-breakdown-bar-chart", "figure"),
    [Input("interval-component", "n_intervals")],
)
def update_demand_breakdown_bar_chart(n_intervals):
    data = fetch_data("get_demand_breakdown")
    df = pd.DataFrame(
        data,
        columns=[
            "Time",
            "Net Demand",
            "Gross Demand",
            "Pumped Storage",
            "Exports",
            "Station Load",
            "Embedded Wind",
            "Embedded Solar",
            "Actual Net",
            "Actual Gross",
        ],
    )
    figure = px.bar(
        df,
        x="Time",
        y=[
            "Net Demand",
            "Gross Demand",
            "Pumped Storage",
            "Exports",
            "Station Load",
            "Embedded Wind",
            "Embedded Solar",
            "Actual Net",
            "Actual Gross",
        ],
        title="Demand Breakdown",
    )
    return figure


if __name__ == "__main__":
    app.run_server(debug=True)
