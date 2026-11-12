"""Hotel search tool: filter hotels by city, stars and price."""

import json
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "raw" / "hotels.json"
VALID_SORTS = ("rating", "price")


def load_hotels() -> list[dict]:
    """Load all hotels from the JSON dataset."""
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as file:
            return json.load(file)

    except FileNotFoundError:
        raise RuntimeError(f"Hotel data not found at {DATA_PATH}")

    except json.JSONDecodeError as error:
        raise RuntimeError(f"Hotel data is not valid JSON: {error}")


def search_hotels(
    city: str,
    min_stars: int = 0,
    max_price: int | None = None,
    sort_by: str = "rating",
) -> list[dict]:
    """Return hotels filtered by city, minimum stars and maximum price.

    sort_by: "rating" = highest stars first (cheaper first on ties).
             "price" = cheapest first.
    """

    # Validate sorting
    if sort_by not in VALID_SORTS:
        raise ValueError(
            f"sort_by must be one of {VALID_SORTS}, got '{sort_by}'"
        )

    # Filter hotels
    matches = [
        hotel for hotel in load_hotels()
        if hotel["city"].lower() == city.lower()
        and hotel["stars"] >= min_stars
        and (
            max_price is None
            or hotel["price_per_night"] <= max_price
        )
    ]

    # Sort hotels
    if sort_by == "rating":
        matches.sort(
            key=lambda h: (-h["stars"], h["price_per_night"])
        )
    else:
        matches.sort(key=lambda h: h["price_per_night"])

    return matches


if __name__ == "__main__":

    print("All hotels in Goa:")
    print(search_hotels("Goa"))

    print("\nGoa hotels (minimum 4 stars, maximum ₹4000):")
    print(search_hotels("goa", min_stars=4, max_price=4000))

    print("\nHotels in Atlantis:")
    print(search_hotels("Atlantis"))
