import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, dcc, html
import pandas as pd
import plotly.express as px
from sqlalchemy.orm import scoped_session, sessionmaker
from data.db import engine
from data.dal import DataAccessLayer

from reports.correlation import get_corr

# Database setup
Session = scoped_session(sessionmaker(bind=engine))

# Choose a Bootswatch theme
BOOTSTRAP_THEME = dbc.themes.FLATLY

app = dash.Dash(__name__, external_stylesheets=[BOOTSTRAP_THEME])

# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

sidebar = html.Div(
    [
        html.H2("Sidebar", className="display-4"),
        html.Hr(),
        html.P("A simple sidebar layout with navigation links", className="lead"),
        dbc.Nav(
            [
                dbc.NavLink("Carbon Intensity", href="/page-1", active="exact"),
                dbc.NavLink("Energy Mix", href="/page-3", active="exact"),
                dbc.NavLink("Weather", href="/page-5", active="exact"),
                dbc.NavLink("Wind Data", href="/page-6", active="exact"),
                dbc.NavLink("Correlation Matrix", href="/page-7", active="exact"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div(id="page-content", style=CONTENT_STYLE)

app.layout = html.Div([dcc.Location(id="url"), sidebar, content])


# Define a function to fetch data from the database
def fetch_data(dal_method):
    with Session() as session:
        dal = DataAccessLayer(session)
        data = getattr(dal, dal_method)()
    return data


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname in ["/", "/page-1"]:
        data = fetch_data("get_carbon_intensity_over_time")
        df = pd.DataFrame(data)
        figure = px.line(
            df, x="start", y="carbon_intensity", title="Carbon Intensity Over Time"
        )
        return html.Div(
            [
                dcc.Markdown(
                    """
                ## Carbon Intensity Over Time
                This graph shows the carbon intensity of electricity generation over time. 
                Lower carbon intensity indicates a cleaner energy mix.
            """
                ),
                dcc.Graph(figure=figure),
            ]
        )
    elif pathname == "/page-3":
        data = fetch_data("get_energy_mix")
        df = pd.DataFrame(data)
        figure = px.pie(
            df, names="type_name", values="total_generation", title="Energy Mix"
        )
        return html.Div(
            [
                dcc.Markdown(
                    """
                ## Energy Mix
                This pie chart displays the proportion of different energy types contributing to the total generation.
                A diverse energy mix can be more resilient and sustainable.
            """
                ),
                dcc.Graph(figure=figure),
            ]
        )
    elif pathname == "/page-5":
        data = fetch_data("get_weather")
        df = pd.DataFrame(data)
        # plot temperature over time
        fig = px.line(df, x="time", y="temp_c", title="Temperature over time")

        # plot wind speed over time
        fig2 = px.line(df, x="time", y="wind_mph", title="Wind speed over time")
        return html.Div(
            [
                dcc.Markdown(
                    """
                ## Weather
                The line charts show the temperature and wind speed over time.
            """
                ),
                dcc.Graph(figure=fig),
                dcc.Graph(figure=fig2),
            ]
        )
    elif pathname == "/page-6":
        data = fetch_data("get_wind_data")
        df = pd.DataFrame(data, columns=["hour", "wind_speed", "wind_generation"])
        figure = px.line(df, x="hour", y="wind_speed", title="Wind Speed Over Time")
        figure2 = px.line(
            df, x="hour", y="wind_generation", title="Wind Energy Generation Over Time"
        )
        return html.Div(
            [
                dcc.Markdown(
                    """
                ## Wind Data
                The line charts show the wind speed and wind energy generation over time.
            """
                ),
                dcc.Graph(figure=figure),
                dcc.Graph(figure=figure2),
            ]
        )
    elif pathname == "/page-7":
        corr = get_corr()

        return html.Div(
            [
                dcc.Markdown(
                    """
                ## Correlation Matrix
                The correlation matrix shows the correlation between weather variables and energy types.
            """
                ),
                corr,
            ]
        )

    # If the user tries to reach a different page, return a 404 message
    return html.Div(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ],
        className="p-3 bg-light rounded-3",
    )


if __name__ == "__main__":
    app.run_server(debug=True)
