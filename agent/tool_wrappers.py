"""LangChain tool wrappers: expose the plain Python tools to the agent.

The docstrings and type hints below are what the LLM reads to decide
when and how to call each tool, so keep them precise.
"""

from langchain_core.tools import tool

from tools.budget import estimate_budget
from tools.flights import find_flight_options
from tools.hotels import search_hotels
from tools.places import search_places
from tools.weather import get_weather


@tool
def flight_search_tool(source: str, destination: str) -> dict:
    """Find flights from a source city to a destination city.

    Returns direct flights (cheapest first). If none exist, returns one-stop
    connections with legs and total_price. If no route exists, returns
    type "none" with a message.

    Args:
        source: Departure city, e.g. "Bangalore".
        destination: Arrival city, e.g. "Goa".
    """
    try:
        return find_flight_options(source, destination)
    except (RuntimeError, ValueError) as error:
        return {"error": str(error)}


@tool
def hotel_search_tool(
    city: str,
    min_stars: int = 0,
    max_price: int | None = None,
    sort_by: str = "rating",
) -> list[dict] | dict:
    """Find hotels in a city. Each hotel has a unique hotel_id; always refer
    to hotels by hotel_id because names can repeat.

    Args:
        city: City name, e.g. "Goa".
        min_stars: Minimum star rating (0-5).
        max_price: Maximum price per night in INR, or null for no limit.
        sort_by: "rating" (most stars first) or "price" (cheapest first).
    """
    try:
        return search_hotels(city, min_stars, max_price, sort_by)
    except (RuntimeError, ValueError) as error:
        return {"error": str(error)}


@tool
def places_search_tool(
    city: str,
    place_type: str | None = None,
    min_rating: float = 0.0,
    limit: int | None = None,
) -> list[dict] | dict:
    """Find tourist attractions in a city, best-rated first.

    Args:
        city: City name, e.g. "Goa".
        place_type: Optional filter, singular form. One of: park, market,
            museum, temple, lake, fort, beach, monument. If the user asks
            for "beaches", pass "beach". Returns an empty list if the city
            has no place of that type; then retry without place_type.
        min_rating: Minimum rating (0-5).
        limit: Maximum number of places to return, or null for all.
    """
    try:
        return search_places(city, place_type, min_rating, limit)
    except (RuntimeError, ValueError) as error:
        return {"error": str(error)}


@tool
def weather_tool(city: str, start_date: str, end_date: str) -> dict:
    """Get the daily weather forecast for a city between two dates.

    Only dates from today up to about 15 days ahead are available. If the
    dates are outside this window an error is returned; tell the user the
    forecast is unavailable instead of inventing weather.

    Args:
        city: City name, e.g. "Goa".
        start_date: First day, format YYYY-MM-DD.
        end_date: Last day, format YYYY-MM-DD.
    """
    return get_weather(city, start_date, end_date)


@tool
def budget_tool(
    flight_cost: float,
    hotel_price_per_night: float,
    trip_days: int,
    daily_expense: float = 800,
) -> dict:
    """Estimate the total trip cost in INR.

    Nights are trip_days - 1. Food and local travel cost daily_expense per day.

    Args:
        flight_cost: Total flight cost for the whole trip (include the return
            flight if one is planned).
        hotel_price_per_night: Price per night of the chosen hotel.
        trip_days: Number of days of the trip.
        daily_expense: Food and local travel per day (default 800).
    """
    return estimate_budget(flight_cost, hotel_price_per_night, trip_days, daily_expense)


ALL_TOOLS = [
    flight_search_tool,
    hotel_search_tool,
    places_search_tool,
    weather_tool,
    budget_tool,
]