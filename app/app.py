import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output
import plotly.express as px
from sqlalchemy.orm import scoped_session, sessionmaker
from db import engine
from dal import DataAccessLayer
import pandas as pd

# Database setup
Session = scoped_session(sessionmaker(bind=engine))

# Choose a Bootswatch theme
BOOTSTRAP_THEME = dbc.themes.FLATLY

app = dash.Dash(__name__, external_stylesheets=[BOOTSTRAP_THEME])


# Define a function to fetch data from the database
def fetch_data(dal_method):
    with Session() as session:
        dal = DataAccessLayer(session)
        data = getattr(dal, dal_method)()
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


# Callback function generator to reduce duplication
def generate_callback(output_component_id, dal_method, figure_generator):
    @app.callback(
        Output(output_component_id, "figure"),
        [Input("interval-component", "n_intervals")],
    )
    def update_graph(n_intervals):
        data = fetch_data(dal_method)
        df = pd.DataFrame(data)
        figure = figure_generator(df)
        return figure

    return update_graph


# Generate callback functions for each graph
update_carbon_intensity_graph = generate_callback(
    "carbon-intensity-graph",
    "get_carbon_intensity_over_time",
    lambda df: px.line(
        df, x="Time", y="Carbon Intensity", title="Carbon Intensity Over Time"
    ),
)

update_demand_generation_graph = generate_callback(
    "demand-generation-graph",
    "get_total_demand_and_generation_over_time",
    lambda df: px.line(
        df,
        x="Time",
        y=["Total Demand", "Total Generation"],
        title="Demand vs Generation Over Time",
    ),
)

update_energy_mix_pie_chart = generate_callback(
    "energy-mix-pie-chart",
    "get_energy_mix",
    lambda df: px.pie(
        df, names="Energy Type", values="Total Generation", title="Energy Mix"
    ),
)

update_demand_breakdown_bar_chart = generate_callback(
    "demand-breakdown-bar-chart",
    "get_demand_breakdown",
    lambda df: px.bar(df, x="Time", y=df.columns[1:], title="Demand Breakdown"),
)

if __name__ == "__main__":
    app.run_server(debug=True)
