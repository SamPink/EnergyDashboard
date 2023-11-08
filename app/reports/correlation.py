import sqlite3
import pandas as pd


# Function to load a full table into a DataFrame
def load_full_table(database_path, table_name):
    conn = sqlite3.connect(database_path)
    query = f"SELECT * FROM {table_name};"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def get_corr():
    # Load the weather dataset from data.db
    df_weather = load_full_table("data.db", "weather")

    # Load the energy data from data_h.db
    df_periods = load_full_table("data.db", "periods")
    df_energy_types = load_full_table("data.db", "energy_types")

    # Convert timestamps to datetime for both energy and weather data
    df_periods["start"] = pd.to_datetime(df_periods["start"])
    df_weather["time"] = pd.to_datetime(df_weather["time"])

    # Merge the periods and energy_types tables on the period_id
    df_energy = pd.merge(
        df_periods, df_energy_types, left_on="id", right_on="period_id"
    )

    # Merge the energy data with the weather data on the closest timestamps
    df_combined = pd.merge_asof(
        df_energy.sort_values("start"),
        df_weather.sort_values("time"),
        left_on="start",
        right_on="time",
        direction="nearest",
    )

    # Pivot the 'type_name' and 'total' to create separate columns for each energy type
    df_pivot_energy = df_combined.pivot_table(
        index=[
            "start",
            "end",
            "time",
            "temp_c",
            "wind_mph",
            "humidity",
            "precip_mm",
            "cloud",
            "uv",
        ],
        columns="type_name",
        values="total",
    ).reset_index()

    # Calculate the correlation matrix for selected weather variables and energy types
    selected_columns = [
        "temp_c",
        "wind_mph",
        "humidity",
        "precip_mm",
        "cloud",
        "uv",
        "Biomass",
        "Coal",
        "Gas",
        "Hydro",
        "Imports",
        "Misc",
        "Nuclear",
        "PSH",
        "Solar",
        "Wind",
    ]
    correlation_matrix = df_pivot_energy[selected_columns].corr()

    # Display the correlations for weather variables with the energy types
    correlations = correlation_matrix.loc[
        ["temp_c", "wind_mph", "humidity", "precip_mm", "cloud", "uv"],
        [
            "Biomass",
            "Coal",
            "Gas",
            "Hydro",
            "Imports",
            "Misc",
            "Nuclear",
            "PSH",
            "Solar",
            "Wind",
        ],
    ]

    return correlations


print(get_corr())
