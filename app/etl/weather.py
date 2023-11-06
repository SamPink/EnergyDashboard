import requests
from sqlalchemy.orm import sessionmaker

# Import your Weather model here
from app.data.db import engine
from ..data.models import Weather

Session = sessionmaker(bind=engine)


def fetch_tomorrows_weather(api_key, location="London"):
    # Define the endpoint for the forecast
    url = (
        f"http://api.weatherapi.com/v1/forecast.json?key={api_key}&q={location}&days=1"
    )

    # Make a GET request to fetch the weather data
    response = requests.get(url)
    if response.status_code == 200:
        # Parse the JSON response
        weather_data = response.json()
        # Extract tomorrow's forecast
        tomorrow_forecast = weather_data["forecast"]["forecastday"][0]
        return tomorrow_forecast
    else:
        print(f"Failed to retrieve data: {response.status_code}")
        return None


def transform_weather_data(daily_forecast):
    return [Weather.from_dict(hour) for hour in daily_forecast]

    # return Weather.from_dict(daily_forecast)


def load_weather_data(weather):
    with Session() as session:
        for entry in weather:
            session.add(entry)
        session.commit()


def run():
    api_key = "dd727529d2a245248d3160947230311"  # Replace with your actual API key

    # Fetch tomorrow's weather forecast
    forecast = fetch_tomorrows_weather(api_key)
    if forecast:
        # write to local json file
        import json

        with open("weather.json", "w") as f:
            json.dump(forecast, f)

        weather = transform_weather_data(forecast["hour"])

        try:
            load_weather_data(weather)
            print("Weather data loaded successfully.")
        except:
            print("Weather data failed to load.")


if __name__ == "__main__":
    run()
