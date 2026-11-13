
"""Places discovery tool: find attractions by city, type and rating."""

import json
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "raw" / "places.json"


def load_places() -> list[dict]:
    """Load all places from the JSON dataset."""
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
    """Return places in a city, best-rated first.

    Filters by city, optional place type and minimum rating.
    Results are sorted by rating (highest first), then name.
    """

    # Filter places
    matches = [
        place for place in load_places()
        if place["city"].lower() == city.lower()
        and place["rating"] >= min_rating
        and (
            place_type is None
            or place["type"].lower() == place_type.lower()
        )
    ]

    # Sort by rating, then name
    matches.sort(
        key=lambda place: (-place["rating"], place["name"].lower())
    )

    # Apply result limit
    return matches[:limit]


if __name__ == "__main__":

    print("All places in Goa:")
    print(search_places("Goa"))

    print("\nBeaches in Goa:")
    print(search_places("Goa", place_type="beach"))

    print("\nTop 2 places in Goa with rating >= 4.5:")
    print(search_places("Goa", min_rating=4.5, limit=2))
