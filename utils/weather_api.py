import requests
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# City coordinates (latitude, longitude) for major Indian cities
CITY_COORDINATES = {
    "Mumbai": [19.0760, 72.8777],
    "Delhi": [28.6139, 77.2090],
    "Bangalore": [12.9716, 77.5946],
    "Hyderabad": [17.3850, 78.4867],
    "Chennai": [13.0827, 80.2707],
    "Kolkata": [22.5726, 88.3639],
    "Pune": [18.5204, 73.8567],
    "Ahmedabad": [23.0225, 72.5714],
    "Jaipur": [26.9124, 75.7873],
    "Surat": [21.1702, 72.8311],
    "Lucknow": [26.8467, 80.9462],
    "Kanpur": [26.4499, 80.3319],
    "Nagpur": [21.1458, 79.0882],
    "Indore": [22.7196, 75.8577],
    "Thane": [19.2183, 72.9781],
    "Bhopal": [23.2599, 77.4126],
    "Visakhapatnam": [17.6868, 83.2185],
    "Patna": [25.5941, 85.1376],
    "Vadodara": [22.3072, 73.1812],
    "Ghaziabad": [28.6692, 77.4538]
}

def get_weather_data(city):
    """
    Get current weather data for a city using Open-Meteo API
    """
    if city not in CITY_COORDINATES:
        raise ValueError(f"City '{city}' is not supported")
    
    lat, lon = CITY_COORDINATES[city]
    
    url = f"https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": True,
        "hourly": "temperature_2m,relativehumidity_2m,precipitation,windspeed_10m"
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Extract current weather data
        current = data.get("current_weather", {})
        
        # Get the current hour's index
        current_time = datetime.fromisoformat(current.get("time", "").replace("Z", ""))
        current_hour_index = None
        
        hourly_time = data.get("hourly", {}).get("time", [])
        for i, time_str in enumerate(hourly_time):
            if time_str == current.get("time"):
                current_hour_index = i
                break
        
        if current_hour_index is not None:
            humidity = data.get("hourly", {}).get("relativehumidity_2m", [])[current_hour_index]
            precipitation = data.get("hourly", {}).get("precipitation", [])[current_hour_index]
        else:
            humidity = None
            precipitation = None
        
        return {
            "city": city,
            "temperature": current.get("temperature"),
            "windspeed": current.get("windspeed"),
            "winddirection": current.get("winddirection"),
            "weathercode": current.get("weathercode"),
            "humidity": humidity,
            "precipitation": precipitation,
            "time": current.get("time"),
            "weather_description": get_weather_description(current.get("weathercode"))
        }
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching weather data for {city}: {str(e)}")
        raise Exception(f"Failed to fetch weather data: {str(e)}")

def get_forecast_data(city):
    """
    Get 5-day weather forecast for a city using Open-Meteo API
    """
    if city not in CITY_COORDINATES:
        raise ValueError(f"City '{city}' is not supported")
    
    lat, lon = CITY_COORDINATES[city]
    
    url = f"https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "weathercode,temperature_2m_max,temperature_2m_min,precipitation_sum",
        "timezone": "auto",
        "forecast_days": 7
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        daily_data = data.get("daily", {})
        
        forecast = []
        for i in range(min(5, len(daily_data.get("time", [])))):
            forecast.append({
                "date": daily_data.get("time", [])[i],
                "weathercode": daily_data.get("weathercode", [])[i],
                "temperature_max": daily_data.get("temperature_2m_max", [])[i],
                "temperature_min": daily_data.get("temperature_2m_min", [])[i],
                "precipitation": daily_data.get("precipitation_sum", [])[i],
                "weather_description": get_weather_description(daily_data.get("weathercode", [])[i])
            })
        
        return forecast
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching forecast data for {city}: {str(e)}")
        raise Exception(f"Failed to fetch forecast data: {str(e)}")

def get_weather_description(code):
    """
    Convert WMO weather code to description
    """
    weather_codes = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Depositing rime fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",
        56: "Light freezing drizzle",
        57: "Dense freezing drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",
        66: "Light freezing rain",
        67: "Heavy freezing rain",
        71: "Slight snow fall",
        73: "Moderate snow fall",
        75: "Heavy snow fall",
        77: "Snow grains",
        80: "Slight rain showers",
        81: "Moderate rain showers",
        82: "Violent rain showers",
        85: "Slight snow showers",
        86: "Heavy snow showers",
        95: "Thunderstorm",
        96: "Thunderstorm with slight hail",
        99: "Thunderstorm with heavy hail"
    }
    
    return weather_codes.get(code, "Unknown")
