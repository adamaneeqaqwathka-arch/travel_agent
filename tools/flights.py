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



def find_flight_options(
    source: str,
    destination: str,
    sort_by: str = "price"
) -> dict:
    """Find direct or one-stop flights, sorted by price or duration."""

    if sort_by not in VALID_SORTS:
        raise ValueError(f"Invalid sort option: {sort_by}")

    # Step 1: Check direct flights
    direct = search_flights(source, destination, sort_by)

    if direct:
        return {"type": "direct", "options": direct}

    # Step 2: Find possible stopover cities
    flights = load_flights()

    all_cities = {f["from"] for f in flights} | {
        f["to"] for f in flights
    }

    stopovers = [
        city for city in all_cities
        if city.lower() not in (source.lower(), destination.lower())
    ]

    connections = []

    for city in stopovers:
        first_legs = search_flights(source, city)
        second_legs = search_flights(city, destination)

        if first_legs and second_legs:

            # Cheapest flight on each leg
            leg1 = first_legs[0]
            leg2 = second_legs[0]

            # Step 3: Validate layover
            departure_leg2 = datetime.fromisoformat(
                leg2["departure_time"]
            )

            arrival_leg1 = datetime.fromisoformat(
                leg1["arrival_time"]
            )

            if departure_leg2 <= arrival_leg1:
                continue

            # Step 4: Calculate total duration
            total_duration = (
                get_duration(leg1) + get_duration(leg2)
            )

            connections.append({
                "via": city,
                "legs": [leg1, leg2],
                "total_price": leg1["price"] + leg2["price"],
                "total_duration": total_duration
            })

    # Step 5: Sort connections
    if connections:
        if sort_by == "price":
            connections.sort(key=lambda c: c["total_price"])
        else:
            connections.sort(key=lambda c: c["total_duration"])

        return {
            "type": "one_stop",
            "options": connections
        }

    return {
        "type": "none",
        "message": (
            f"No direct or valid one-stop route "
            f"from {source} to {destination}"
        )
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