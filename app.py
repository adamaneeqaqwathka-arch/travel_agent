"""Streamlit UI for the Agentic AI Travel Planning Assistant.

Run with:  streamlit run app.py
"""

from datetime import date, timedelta

import streamlit as st

from agent.agent import plan_trip
from agent.formatting import itinerary_to_text
from agent.schemas import Itinerary

CITIES = ["Bangalore", "Chennai", "Delhi", "Goa", "Hyderabad", "Jaipur", "Kolkata", "Mumbai"]
PLACE_TYPES = ["Any", "beach", "temple", "museum", "fort", "park", "market", "lake", "monument"]
MAX_FORECAST_DAYS = 15


def build_query(source, destination, start, days, min_stars, max_hotel_price, place_type, notes):
    """Turn the form values into one natural-language request for the agent."""
    end = start + timedelta(days=days - 1)
    parts = [
        f"Plan a {days}-day trip from {source} to {destination}, "
        f"from {start.isoformat()} to {end.isoformat()}.",
        f"Hotel must be at least {min_stars} stars." if min_stars else "",
        f"Hotel price must be at most {max_hotel_price} INR per night." if max_hotel_price else "",
        f"I would like to visit places of type {place_type}." if place_type != "Any" else "",
        notes.strip(),
    ]
    return " ".join(p for p in parts if p)


def show_itinerary(trip: Itinerary) -> None:
    """Render the structured itinerary with simple widgets."""
    if trip.clarification_question:
        st.info(trip.clarification_question)
        return

    st.subheader(trip.title or "Your Trip")
    st.write(trip.summary)

    if trip.budget:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Flight", f"₹{trip.budget.flight_inr:,.0f}")
        c2.metric(f"Hotel ({trip.budget.nights} nights)", f"₹{trip.budget.hotel_inr:,.0f}")
        c3.metric("Food & travel", f"₹{trip.budget.food_and_travel_inr:,.0f}")
        c4.metric("Total", f"₹{trip.budget.total_inr:,.0f}")

    left, right = st.columns(2)
    if trip.flight:
        f = trip.flight
        left.markdown("**Flight**")
        left.write(f"{f.airlines}: {f.route} ({'direct' if f.stops == 0 else f'{f.stops} stop'}), "
                   f"₹{f.price_inr:,.0f}")
        if f.note:
            left.caption(f.note)
    if trip.hotel:
        h = trip.hotel
        right.markdown("**Hotel**")
        right.write(f"{h.name} ({h.stars}-star), ₹{h.price_per_night_inr:,.0f}/night")
        right.caption(f"Hotel ID: {h.hotel_id}")

    if trip.days:
        st.markdown("**Day-wise plan**")
        for d in trip.days:
            with st.expander(f"Day {d.day} ({d.date})", expanded=True):
                st.write("Places: " + (", ".join(d.places) or "Free day"))
                st.write("Weather: " + d.weather)

    if trip.reasoning:
        st.markdown("**Why these choices**")
        for reason in trip.reasoning:
            st.write(f"- {reason}")
    for note in trip.notes:
        st.warning(note)


def main() -> None:
    st.set_page_config(page_title="AI Travel Planner", page_icon="✈️", layout="centered")
    st.title("✈️ AI Travel Planner")
    st.caption("An agent that searches flights, hotels, places and live weather to plan your trip.")

    with st.form("trip_form"):
        col1, col2 = st.columns(2)
        source = col1.selectbox("From", CITIES, index=CITIES.index("Bangalore"))
        destination = col2.selectbox("To", CITIES, index=CITIES.index("Goa"))
        col3, col4 = st.columns(2)
        today = date.today()
        start = col3.date_input("Start date", value=today + timedelta(days=2),
                                min_value=today,
                                max_value=today + timedelta(days=MAX_FORECAST_DAYS - 1),
                                help="Live weather is available for about 15 days ahead.")
        days = col4.slider("Trip length (days)", 1, 7, 3)
        col5, col6 = st.columns(2)
        min_stars = col5.slider("Minimum hotel stars", 0, 5, 0)
        max_hotel_price = col6.number_input("Max hotel price per night (₹, 0 = no limit)",
                                            min_value=0, value=0, step=500)
        place_type = st.selectbox("Preferred place type", PLACE_TYPES)
        notes = st.text_area("Anything else?", placeholder="e.g. prefer the cheapest options")
        submitted = st.form_submit_button("Plan my trip", type="primary")

    if not submitted:
        return
    if source == destination:
        st.error("Source and destination must be different.")
        return

    query = build_query(source, destination, start, days, min_stars,
                        max_hotel_price, place_type, notes)
    try:
        with st.spinner("Planning your trip. This can take up to a minute..."):
            trip = plan_trip(query)
    except Exception as error:  # LLM/API/network failures should not crash the UI
        st.error("The planning service had a problem. Please try again in a moment.")
        with st.expander("Technical details"):
            st.code(str(error))
        return

    tab_plan, tab_text, tab_json = st.tabs(["Itinerary", "Text", "JSON"])
    with tab_plan:
        show_itinerary(trip)
    with tab_text:
        st.text(itinerary_to_text(trip))
    with tab_json:
        json_text = trip.model_dump_json(indent=2)
        st.download_button("Download JSON", json_text, file_name="itinerary.json",
                           mime="application/json")
        st.code(json_text, language="json")


if __name__ == "__main__":
    main()
