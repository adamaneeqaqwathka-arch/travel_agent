"""Flight search tool: direct flights first, then one-stop connections."""

import json
from datetime import datetime, timedelta
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent / "data" /"raw" / "flights.json"
VALID_SORTS = ("price", "duration")


def load_flights() -> list[dict]:
    """Load all flights from the JSON dataset.

    Raises:
        RuntimeError: if the file is missing or contains invalid JSON.
    """
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        raise RuntimeError(f"Flight data not found at {DATA_PATH}")
    except json.JSONDecodeError as error:
        raise RuntimeError(f"Flight data is not valid JSON: {error}")


def get_duration(flight: dict) -> timedelta:
    """Return a flight's duration as a timedelta."""
    departure = datetime.fromisoformat(flight["departure_time"])
    arrival = datetime.fromisoformat(flight["arrival_time"])
    return arrival - departure


def search_flights(source: str, destination: str, sort_by: str = "price") -> list[dict]:
    """Return direct flights from source to destination.

    Matching ignores upper/lower case. Results are sorted by 'price'
    (default) or 'duration'.
    """
    if sort_by not in VALID_SORTS:
        raise ValueError(f"sort_by must be one of {VALID_SORTS}, got '{sort_by}'")

    matches = [
        flight for flight in load_flights()
        if flight["from"].lower() == source.lower()
        and flight["to"].lower() == destination.lower()
    ]
    key = (lambda f: f["price"]) if sort_by == "price" else get_duration
    return sorted(matches, key=key)


def find_flight_options(source: str, destination: str) -> dict:
    """Find direct flights, or one-stop connections if none exist.

    Dates are ignored when pairing legs: the dataset's flights are treated
    as representative schedules for each route, and the cheapest flight on
    each leg is used.

    Returns one of three shapes:
        {"type": "direct",   "options": [flight, ...]}
        {"type": "one_stop", "options": [{"via", "legs", "total_price"}, ...]}
        {"type": "none",     "message": "..."}
    """
    direct = search_flights(source, destination)
    if direct:
        return {"type": "direct", "options": direct}

    flights = load_flights()
    all_cities = {f["from"] for f in flights} | {f["to"] for f in flights}
    stopovers = [
        city for city in all_cities
        if city.lower() not in (source.lower(), destination.lower())
    ]

    connections = []
    for city in stopovers:
        first_legs = search_flights(source, city)
        second_legs = search_flights(city, destination)
        if first_legs and second_legs:
            leg1, leg2 = first_legs[0], second_legs[0]  # cheapest of each
            connections.append({
                "via": city,
                "legs": [leg1, leg2],
                "total_price": leg1["price"] + leg2["price"],
            })

    if connections:
        connections.sort(key=lambda c: c["total_price"])
        return {"type": "one_stop", "options": connections}

    return {
        "type": "none",
        "message": f"No direct or one-stop route from {source} to {destination}",
    }


if __name__ == "__main__":
    for src, dst in [("Mumbai", "Goa"), ("Bangalore", "Hyderabad"), ("Delhi", "Bangalore")]:
        result = find_flight_options(src, dst)
        print(f"\n{src} -> {dst}: {result['type']}")
        if result["type"] == "one_stop":
            for option in result["options"]:
                print(f"  via {option['via']}: Rs {option['total_price']}")
        elif result["type"] == "direct":
            print(f"  cheapest: {result['options'][0]['airline']} Rs {result['options'][0]['price']}")
        else:
            print(" ", result["message"])