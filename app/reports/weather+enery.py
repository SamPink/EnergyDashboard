import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# Connect to the SQLite database
db_path = "data.db"
conn = sqlite3.connect(db_path)

# Extract necessary data from 'weather' table for today up until 2pm
weather_data_query = """
SELECT 
    strftime('%Y-%m-%d %H:%M:%S', time) as time, 
    wind_mph 
FROM 
    weather 
WHERE 
    time(time) <= time('14:00:00') AND 
    date(time) = date('now', 'localtime');
"""
weather_data = pd.read_sql_query(weather_data_query, conn)

# Extract wind energy generation data from 'energy_types' table
wind_energy_data_query = """
SELECT 
    p.id as period_id, 
    p.start,
    p.end, 
    e.type_name, 
    e.total as wind_generation
FROM 
    periods p 
JOIN 
    energy_types e ON p.id = e.period_id
WHERE 
    e.type_name LIKE '%Wind%' AND 
    date(p.start) = date('now', 'localtime');
"""
wind_energy_data = pd.read_sql_query(wind_energy_data_query, conn)

# Convert the 'start' and 'end' times to datetime to facilitate aggregation
wind_energy_data["start"] = pd.to_datetime(wind_energy_data["start"])
wind_energy_data["end"] = pd.to_datetime(wind_energy_data["end"])

# Calculate the hour for each period to facilitate aggregation
wind_energy_data["hour"] = wind_energy_data["start"].dt.hour

# Aggregate wind energy generation by hour
hourly_wind_generation = (
    wind_energy_data.groupby("hour").agg({"wind_generation": "sum"}).reset_index()
)

# Join the weather data with the aggregated wind generation data on the hour
weather_data["hour"] = pd.to_datetime(weather_data["time"]).dt.hour
combined_data = pd.merge(weather_data, hourly_wind_generation, on="hour", how="left")

# Calculate the correlation between wind speed and wind generation
correlation = combined_data[["wind_mph", "wind_generation"]].corr().iloc[0, 1]

# Plot wind speed and wind energy generation on separate y-axes
fig, ax1 = plt.subplots()

color = "tab:red"
ax1.set_xlabel("Hour of the Day")
ax1.set_ylabel("Wind Speed (mph)", color=color)
ax1.plot(combined_data["hour"], combined_data["wind_mph"], color=color)
ax1.tick_params(axis="y", labelcolor=color)

ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

color = "tab:blue"
ax2.set_ylabel(
    "Wind Energy Generation (MWh)", color=color
)  # we already handled the x-label with ax1
ax2.plot(combined_data["hour"], combined_data["wind_generation"], color=color)
ax2.tick_params(axis="y", labelcolor=color)

fig.tight_layout()  # otherwise the right y-label is slightly clipped
plt.title("Wind Speed and Wind Energy Generation by Hour")
plt.show()
