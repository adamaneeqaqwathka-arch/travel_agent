"""Weather lookup tool: daily forecast from the free Open-Meteo API."""

from datetime import date, timedelta

import requests

FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
MAX_FORECAST_DAYS = 16  # Open-Meteo forecasts reach about 16 days ahead

CITY_COORDINATES = {
    "delhi": (28.6139, 77.2090),
    "mumbai": (19.0760, 72.8777),
    "goa": (15.2993, 74.1240),
    "bangalore": (12.9716, 77.5946),
    "chennai": (13.0827, 80.2707),
    "hyderabad": (17.3850, 78.4867),
    "kolkata": (22.5726, 88.3639),
    "jaipur": (26.9124, 75.7873),
}

# WMO weather codes -> readable text
WEATHER_CODES = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Depositing rime fog",
    51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
    61: "Light rain", 63: "Moderate rain", 65: "Heavy rain",
    80: "Light rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
    95: "Thunderstorm", 96: "Thunderstorm with hail", 99: "Thunderstorm with heavy hail",
}


def get_weather(city: str, start_date: str, end_date: str) -> dict:
    """Return the daily weather forecast for a city between two dates.

    Args:
        city: One of Delhi, Mumbai, Goa, Bangalore, Chennai, Hyderabad,
            Kolkata, Jaipur (case-insensitive).
        start_date: First travel day, format YYYY-MM-DD.
        end_date: Last travel day, format YYYY-MM-DD.

    Returns:
        {"city": ..., "days": [{"date", "max_temp_c", "min_temp_c", "condition"}]}
        or {"error": "..."} if the city is unknown, the dates are outside
        the forecast window, or the API call fails.
    """
    # 1. Coordinates
    coordinates = CITY_COORDINATES.get(city.strip().lower())
    if coordinates is None:
        return {"error": f"Unknown city '{city}'. Supported: "
                         f"{', '.join(c.title() for c in CITY_COORDINATES)}"}
    latitude, longitude = coordinates

    # 2. Date validation
    try:
        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date)
    except ValueError:
        return {"error": "Dates must be in YYYY-MM-DD format."}

    today = date.today()
    last_available = today + timedelta(days=MAX_FORECAST_DAYS - 1)
    if end < start:
        return {"error": "end_date must not be before start_date."}
    if start < today or end > last_available:
        return {"error": f"Forecast is only available from {today} to "
                         f"{last_available}. Requested {start} to {end}."}

    # 3-4. API call
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "timezone": "auto",
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "daily": "temperature_2m_max,temperature_2m_min,weathercode",
    }
    try:
        response = requests.get(FORECAST_URL, params=params, timeout=10)
        response.raise_for_status()
        daily = response.json()["daily"]
    except requests.RequestException as error:
        return {"error": f"Weather service request failed: {error}"}
    except (KeyError, ValueError):
        return {"error": "Weather service returned an unexpected response."}

    # 5. Reshape column lists into one dictionary per day
    days = [
        {
            "date": day,
            "max_temp_c": max_temp,
            "min_temp_c": min_temp,
            "condition": WEATHER_CODES.get(code, f"Weather code {code}"),
        }
        for day, max_temp, min_temp, code in zip(
            daily["time"],
            daily["temperature_2m_max"],
            daily["temperature_2m_min"],
            daily["weathercode"],
        )
    ]
    return {"city": city.title(), "days": days}


if __name__ == "__main__":
    today = date.today()
    print(get_weather("Goa", str(today), str(today + timedelta(days=2))))
    print(get_weather("Atlantis", str(today), str(today)))   # unknown city
    print(get_weather("Goa", "2025-02-12", "2025-02-14"))    # past dates
