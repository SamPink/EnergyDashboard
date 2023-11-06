import requests
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ...data.models import Weather

import datetime


def fetch_weather():
    api_key = "dd727529d2a245248d3160947230311"
    # Determine the end date (today) and start date (two months ago)
    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=1)

    # Create a list of dates between start_date and end_date
    date_list = [
        start_date + datetime.timedelta(days=x)
        for x in range(0, (end_date - start_date).days)
    ]

    all_weather_data = []

    # Iterate over each date and fetch the weather data
    for date in date_list:
        formatted_date = date.strftime("%Y-%m-%d")
        url = f"http://api.weatherapi.com/v1/history.json?key={api_key}&q=London&dt={formatted_date}"
        response = requests.get(url)
        if response.status_code == 200:
            # Get the historical data for the day
            daily_data = response.json()
            all_weather_data.extend(daily_data["forecast"]["forecastday"][0]["hour"])
        else:
            print(
                f"Failed to retrieve data for {formatted_date}: {response.status_code}"
            )

    # Return all collected hourly data
    return all_weather_data


def transform_weather_data(hourly_forecasts):
    # Assuming Weather.from_dict can handle individual hour data and create an instance of the Weather model
    return [Weather.from_dict(hour) for hour in hourly_forecasts]


def load_weather_data(weathers, session):
    for weather in weathers:
        # Merge the 'weather' instance into the session. If a record with the same identifier already exists, it will be updated.
        session.merge(weather)
    session.commit()


def run():
    # get the folder of this file
    import os

    path = os.path.dirname(os.path.abspath(__file__))

    # read hourly_forecasts from a file from this folder
    with open(path + "/hourly_forecasts.json") as f:
        hourly_forecasts = json.load(f)

    if hourly_forecasts:
        weathers = transform_weather_data(hourly_forecasts)

        # Set up database connection
        engine = create_engine("sqlite:///data.db")
        Session = sessionmaker(bind=engine)
        session = Session()

        try:
            load_weather_data(weathers, session)
            print("Weather data loaded successfully.")
        except Exception as e:
            session.rollback()
            print(f"An error occurred: {e}")
        finally:
            session.close()
