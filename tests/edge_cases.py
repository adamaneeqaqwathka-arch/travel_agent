"""Run hard queries through the real agent and print the results.

Usage (from the project root):  python -m scripts.edge_cases
Each case checks that the agent handles a tricky situation honestly.
"""

from datetime import date, timedelta

from agent.agent import plan_trip
from agent.formatting import itinerary_to_text

START = (date.today() + timedelta(days=2)).isoformat()

CASES = {
    "No route in the data (Delhi -> Goa)":
        f"Plan a 3-day trip from Delhi to Goa starting {START}.",
    "One-stop connection (Bangalore -> Hyderabad)":
        f"Plan a 3-day trip from Bangalore to Hyderabad starting {START}.",
    "Not enough places for the days (7 days)":
        f"Plan a 7-day trip from Bangalore to Goa starting {START}.",
    "Requested place type missing in the city (beaches in Goa)":
        f"Plan a 3-day trip from Bangalore to Goa starting {START}. I want beaches.",
    "Tight hotel budget":
        f"Plan a 3-day trip from Mumbai to Goa starting {START}. Hotel under 500 rupees a night.",
    "Dates beyond the weather window":
        "Plan a 3-day trip from Bangalore to Goa starting 2027-03-10.",
    "Missing information":
        "Plan me a trip to Goa.",
}

if __name__ == "__main__":
    for name, query in CASES.items():
        print("=" * 70)
        print(name)
        print("Q:", query)
        print("-" * 70)
        try:
            print(itinerary_to_text(plan_trip(query)))
        except Exception as error:  # keep going even if one case fails
            print("FAILED:", error)