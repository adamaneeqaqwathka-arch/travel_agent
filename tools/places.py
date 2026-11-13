"""Places discovery tool: find attractions by city, type and rating."""

import json
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "raw" / "places.json"


def load_places() -> list[dict]:
    """Load all places from the JSON dataset."""
    # TODO 1: same try/except pattern as load_hotels()


def search_places(
    city: str,
    place_type: str | None = None,
    min_rating: float = 0.0,
    limit: int | None = None,
) -> list[dict]:
    """Return places in a city, best-rated first."""
    # TODO 2: filter by city (case-insensitive)
    #         AND rating >= min_rating
    #         AND (place_type is None OR the place's type matches, case-insensitive)

    # TODO 3: sort by rating, highest first
    #         (tie-breaker idea: name, so results are stable)

    # TODO 4: return matches[:limit]   <- think about what this does when limit is None


if __name__ == "__main__":
    print(search_places("Goa"))
    print(search_places("Goa", place_type="beach"))
    print(search_places("Goa", min_rating=4.5, limit=2))
