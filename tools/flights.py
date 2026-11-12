import json
from pathlib import Path
from datetime import datetime

# Load flight data
DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "flights.json"

with open(DATA_PATH, "r") as f:
    flights = json.load(f)


def search_flights(source, destination, sort_by=None):

    # 1. Filter flights by source and destination
    matching_flights = [
        flight for flight in flights
        if flight["from"].lower() == source.lower()
        and flight["to"].lower() == destination.lower()
    ]

    # 2. Sort by price
    if sort_by == "price":
        matching_flights = sorted(
            matching_flights,
            key=lambda flight: flight["price"]
        )

    # 3. Sort by duration
    elif sort_by == "duration":

        def get_duration(flight):
            dep = datetime.fromisoformat(flight["departure_time"])
            arr = datetime.fromisoformat(flight["arrival_time"])
            return arr - dep

        matching_flights = sorted(
            matching_flights,
            key=get_duration
        )

    # 4. Return results
    return matching_flights


# Test the function
if __name__ == "__main__":

    print("Mumbai to Goa:")
    print(search_flights("Mumbai", "Goa"))

    print("\nGoa to Bangalore (cheapest first):")
    print(search_flights("goa", "bangalore", "price"))

    print("\nDelhi to Goa:")
    print(search_flights("Delhi", "Goa"))