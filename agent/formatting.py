"""Turn a structured Itinerary into human-readable text."""

from agent.schemas import Itinerary


def itinerary_to_text(trip: Itinerary) -> str:
    """Render an Itinerary as readable markdown-style text."""
    if trip.clarification_question:
        return trip.clarification_question

    lines = [f"# {trip.title or 'Your Trip'}", "", trip.summary, ""]

    if trip.flight:
        f = trip.flight
        stops = "direct" if f.stops == 0 else f"{f.stops} stop"
        lines += ["## Flight Selected",
                  f"- {f.airlines}: {f.route} ({stops}), ₹{f.price_inr:,.0f}"
                  + (f" ({f.note})" if f.note else ""), ""]

    if trip.hotel:
        h = trip.hotel
        lines += ["## Hotel Recommendation",
                  f"- {h.name} [{h.hotel_id}], {h.stars}-star, "
                  f"₹{h.price_per_night_inr:,.0f}/night", ""]

    if trip.days:
        lines += ["## Weather"]
        lines += [f"- Day {d.day} ({d.date}): {d.weather}" for d in trip.days]
        lines += ["", "## Day-wise Itinerary"]
        lines += [f"- Day {d.day}: {', '.join(d.places) or 'Free day'}" for d in trip.days]
        lines.append("")

    if trip.budget:
        b = trip.budget
        lines += ["## Budget Breakdown",
                  f"- Flight: ₹{b.flight_inr:,.0f}",
                  f"- Hotel ({b.nights} nights): ₹{b.hotel_inr:,.0f}",
                  f"- Food & Travel: ₹{b.food_and_travel_inr:,.0f}",
                  "- " + "-" * 30,
                  f"- Total: ₹{b.total_inr:,.0f}", ""]

    if trip.reasoning:
        lines += ["## Why These Choices"] + [f"- {r}" for r in trip.reasoning] + [""]

    if trip.notes:
        lines += ["## Notes"] + [f"- {n}" for n in trip.notes]

    return "\n".join(lines).strip()