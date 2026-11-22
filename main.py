"""Command-line entry point: python main.py "Plan a 3-day trip from Bangalore to Goa"."""

import sys

from agent.agent import plan_trip

if __name__ == "__main__":
    query = " ".join(sys.argv[1:]) or "Plan a 3 day trip from Bangalore to Goa starting in 3 days."
    print(plan_trip(query, verbose=True))