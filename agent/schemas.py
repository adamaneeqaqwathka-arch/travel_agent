"""Pydantic schemas for the structured itinerary the agent returns."""

from pydantic import BaseModel, Field


class FlightChoice(BaseModel):
    """The selected flight (direct or one-stop)."""

    route: str = Field(description="e.g. 'Bangalore -> Goa' or 'Bangalore -> Mumbai -> Goa'")
    airlines: str = Field(description="Airline(s) used, e.g. 'SpiceJet' or 'IndiGo, Air India'")
    price_inr: float = Field(description="Total flight cost counted in the budget, in INR")
    stops: int = Field(description="0 for a direct flight, 1 for a one-stop connection")
    note: str = Field(default="", description="Short note, e.g. 'one-way price doubled for return'")


class HotelChoice(BaseModel):
    """The selected hotel."""

    hotel_id: str = Field(description="Unique hotel id from the data, e.g. HOT0014")
    name: str
    stars: int
    price_per_night_inr: float


class DayPlan(BaseModel):
    """One day of the itinerary."""

    day: int = Field(description="Day number starting at 1")
    date: str = Field(description="YYYY-MM-DD")
    places: list[str] = Field(description="Place names to visit that day (from the tool data)")
    weather: str = Field(description="Weather for the day, or 'Forecast unavailable'")


class BudgetBreakdown(BaseModel):
    """Cost breakdown copied from the budget tool."""

    flight_inr: float
    hotel_inr: float
    nights: int
    food_and_travel_inr: float
    total_inr: float


class Itinerary(BaseModel):
    """The complete trip plan. If key details are missing, only fill
    clarification_question and leave the other sections empty."""

    title: str = Field(default="", description="e.g. 'Your 3-Day Trip to Goa'")
    summary: str = Field(default="", description="Two-sentence trip summary")
    flight: FlightChoice | None = None
    hotel: HotelChoice | None = None
    days: list[DayPlan] = Field(default_factory=list)
    budget: BudgetBreakdown | None = None
    reasoning: list[str] = Field(
        default_factory=list,
        description="Short 'why we chose this' points for flight, hotel and places",
    )
    notes: list[str] = Field(
        default_factory=list,
        description="Caveats: no route, forecast unavailable, not enough places, etc.",
    )
    clarification_question: str | None = Field(
        default=None,
        description="Set only if the request lacks source city or trip length",
    )