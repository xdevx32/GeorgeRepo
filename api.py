# generate the request response logic for making a call to windy.com api and retrieving current temeperature, current forecast, forecast for tomorrow, forecast for two days ahead, forecast for the whole week, forecast for the month, forecast for the year.
import requests
from datetime import datetime, timedelta

# Windy.com API endpoint and your API key
API_ENDPOINT = "https://api.windy.com/api/point-forecast/v2"
API_KEY = "YOUR_API_KEY_HERE"  # Replace with your actual Windy.com API key

def get_forecast(lat, lon, parameters, days=1):
    """
    Make a request to the Windy.com API and return the forecast data.
    
    :param lat: Latitude of the location
    :param lon: Longitude of the location
    :param parameters: List of weather parameters to retrieve
    :param days: Number of days to forecast (default is 1)
    :return: JSON response from the API
    """
    payload = {
        "lat": lat,
        "lon": lon,
        "model": "gfs",
        "parameters": parameters,
        "levels": ["surface"],
        "key": API_KEY
    }
    
    response = requests.post(API_ENDPOINT, json=payload)
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API request failed with status code {response.status_code}")

def parse_forecast(data, parameter):
    """
    Parse the forecast data for a specific parameter.
    
    :param data: JSON data from the API response
    :param parameter: The weather parameter to parse
    :return: List of (timestamp, value) tuples
    """
    timestamps = data[parameter]['hours']
    values = data[parameter]['surface']
    return list(zip(timestamps, values))

def get_forecasts(lat, lon):
    """
    Retrieve and organize various forecasts.
    
    :param lat: Latitude of the location
    :param lon: Longitude of the location
    :return: Dictionary containing different forecasts
    """
    parameters = ["temp", "precip", "wind"]
    
    # Get forecast data for the next 7 days (maximum allowed by the free tier)
    data = get_forecast(lat, lon, parameters, days=7)
    
    current_time = datetime.now()
    tomorrow = current_time + timedelta(days=1)
    day_after_tomorrow = current_time + timedelta(days=2)
    
    forecasts = {
        "current_temperature": parse_forecast(data, "temp")[0][1],
        "current_forecast": {param: parse_forecast(data, param)[0] for param in parameters},
        "tomorrow_forecast": {param: next((t, v) for t, v in parse_forecast(data, param) if datetime.fromtimestamp(t) > tomorrow), None) for param in parameters},
        "day_after_tomorrow_forecast": {param: next((t, v) for t, v in parse_forecast(data, param) if datetime.fromtimestamp(t) > day_after_tomorrow), None) for param in parameters},
        "week_forecast": {param: parse_forecast(data, param)[:7*24] for param in parameters},  # 7 days * 24 hours
    }
    
    return forecasts

# Example usage
latitude = 40.7128  # New York City latitude
longitude = -74.0060  # New York City longitude

try:
    forecast_data = get_forecasts(latitude, longitude)
    print(f"Current Temperature: {forecast_data['current_temperature']}°C")
    print(f"Tomorrow's Temperature: {forecast_data['tomorrow_forecast']['temp'][1]}°C")
    print(f"Day After Tomorrow's Temperature: {forecast_data['day_after_tomorrow_forecast']['temp'][1]}°C")
    # Add more print statements to display other forecast information as needed
except Exception as e:
    print(f"An error occurred: {str(e)}")
