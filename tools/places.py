"""Places discovery tool: find attractions by city, type and rating."""

import json
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "raw" / "places.json"


def load_places() -> list[dict]:
    """Load all places from the JSON dataset.

    Raises:
        RuntimeError: if the file is missing or contains invalid JSON.
    """
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        raise RuntimeError(f"Places data not found at {DATA_PATH}")
    except json.JSONDecodeError as error:
        raise RuntimeError(f"Places data is not valid JSON: {error}")


def search_places(
    city: str,
    place_type: str | None = None,
    min_rating: float = 0.0,
    limit: int | None = None,
) -> list[dict]:
    """Return attractions in a city, best-rated first.

    Args:
        city: City name, e.g. "Goa" (case-insensitive).
        place_type: Optional filter. One of: park, market, museum, temple,
            lake, fort, beach, monument. Use the singular form.
        min_rating: Minimum rating (0-5) a place must have.
        limit: Maximum number of places to return (None = all).
    """
    matches = [
        place for place in load_places()
        if place["city"].lower() == city.lower()
        and place["rating"] >= min_rating
        and (place_type is None or place["type"].lower() == place_type.lower())
    ]
    matches.sort(key=lambda p: (-p["rating"], p["name"]))
    return matches[:limit]


if __name__ == "__main__":
    print("All places in Goa:")
    for p in search_places("Goa"):
        print(" ", p["place_id"], p["name"], p["type"], p["rating"])

    print("\nBeaches in Goa:")
    print(search_places("Goa", place_type="beach"))

    print("\nGoa, rating >= 4.5, top 2:")
    print(search_places("goa", min_rating=4.5, limit=2))

    print("\nUnknown city:")
    print(search_places("Atlantis"))