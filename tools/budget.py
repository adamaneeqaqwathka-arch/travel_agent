"""Budget estimation tool: total trip cost from flight, hotel and daily spend."""

DEFAULT_DAILY_EXPENSE = 800  # food + local transport per day, in INR


def estimate_budget(
    flight_cost: float,
    hotel_price_per_night: float,
    trip_days: int,
    daily_expense: float = DEFAULT_DAILY_EXPENSE,
) -> dict:
    """Estimate the total cost of a trip.

    Args:
        flight_cost: Total flight cost for the whole trip, in INR.
        hotel_price_per_night: Hotel price per night, in INR.
        trip_days: Number of days of the trip (nights = trip_days - 1).
        daily_expense: Food and local travel per day, in INR.

    Returns:
        A dict with each cost line and the total, or {"error": "..."}.
    """
    if trip_days < 1:
        return {"error": "trip_days must be at least 1."}
    if min(flight_cost, hotel_price_per_night, daily_expense) < 0:
        return {"error": "Costs must not be negative."}

    nights = trip_days - 1
    hotel_total = hotel_price_per_night * nights
    local_total = daily_expense * trip_days
    total = flight_cost + hotel_total + local_total

    return {
        "flight": round(flight_cost),
        "hotel": round(hotel_total),
        "nights": nights,
        "food_and_travel": round(local_total),
        "total": round(total),
    }


if __name__ == "__main__":
    print(estimate_budget(4800, 3200, 3))   # hotel 6400, total 13600
    print(estimate_budget(4800, 3200, 0))   # error: trip_days
    print(estimate_budget(-1, 3200, 3))     # error: negative cost
    print(estimate_budget(4800, 3200, 1))   # day trip: 0 nights
