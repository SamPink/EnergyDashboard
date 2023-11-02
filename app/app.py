# Import necessary libraries
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
from dash.dependencies import Input, Output
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dal import DataAccessLayer  # Make sure to implement this
import pandas as pd

# Database setup
engine = create_engine("sqlite:///generation.db")
Session = sessionmaker(bind=engine)

# Create a Dash application
app = dash.Dash(__name__)

# Define the layout of the application
app.layout = html.Div(
    children=[
        html.H1(children="Energy Generation Dashboard"),
        # Interval component to trigger callbacks
        dcc.Interval(
            id="interval-component",
            interval=1 * 60000,  # in milliseconds
            n_intervals=0,
        ),
        # Carbon Intensity Over Time Graph
        dcc.Graph(id="carbon-intensity-graph"),
        # Total Demand and Generation Over Time Graph
        dcc.Graph(id="demand-generation-graph"),
        # Energy Mix Pie Chart
        dcc.Graph(id="energy-mix-pie-chart"),
        # Demand Breakdown Bar Chart
        dcc.Graph(id="demand-breakdown-bar-chart"),
        # Add other components like dropdowns or date pickers if needed
        # ...
    ]
)


# Callback for Carbon Intensity Over Time Graph
@app.callback(
    Output("carbon-intensity-graph", "figure"),
    [Input("interval-component", "n_intervals")],
)
def update_carbon_intensity_graph(n_intervals):
    session = Session()
    dal = DataAccessLayer(session)
    data = dal.get_carbon_intensity_over_time()
    df = pd.DataFrame(data, columns=["Time", "Carbon Intensity"])
    figure = px.line(
        df, x="Time", y="Carbon Intensity", title="Carbon Intensity Over Time"
    )
    session.close()
    return figure


# Callback for Total Demand and Generation Over Time Graph
@app.callback(
    Output("demand-generation-graph", "figure"),
    [Input("interval-component", "n_intervals")],
)
def update_demand_generation_graph(n_intervals):
    session = Session()
    dal = DataAccessLayer(session)
    data = dal.get_total_demand_and_generation_over_time()
    df = pd.DataFrame(data, columns=["Time", "Total Demand", "Total Generation"])
    figure = px.line(
        df,
        x="Time",
        y=["Total Demand", "Total Generation"],
        title="Demand vs Generation Over Time",
    )
    session.close()
    return figure


# Callback for Energy Mix Pie Chart
@app.callback(
    Output("energy-mix-pie-chart", "figure"),
    [Input("interval-component", "n_intervals")],
)
def update_energy_mix_pie_chart(n_intervals):
    session = Session()
    dal = DataAccessLayer(session)
    data = dal.get_energy_mix()
    df = pd.DataFrame(data, columns=["Energy Type", "Total Generation"])
    figure = px.pie(
        df, values="Total Generation", names="Energy Type", title="Energy Mix"
    )
    session.close()
    return figure


# Callback for Demand Breakdown Bar Chart
@app.callback(
    Output("demand-breakdown-bar-chart", "figure"),
    [Input("interval-component", "n_intervals")],
)
def update_demand_breakdown_bar_chart(n_intervals):
    session = Session()
    dal = DataAccessLayer(session)
    data = dal.get_demand_breakdown()

    """ Period.start,
                Demand.net,
                Demand.gross,
                Demand.pumped_storage,
                Demand.exports,
                Demand.station_load,
                Demand.embedded_wind,
                Demand.embedded_solar,
                Demand.actual_net,
                Demand.actual_gross, """
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
    session.close()
    return figure


# Run the Dash app
if __name__ == "__main__":
    app.run_server(debug=True)
