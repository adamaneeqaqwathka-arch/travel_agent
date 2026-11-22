import json

with open("data/flights.json") as f:
    flights = json.load(f)

# 1. Print every flight from Goa
goa_flights = [flight for flight in flights if flight["from"] == "Goa"]

print("Flights from Goa:")
for flight in goa_flights:
    print(flight)

print("Total flights from Goa:", len(goa_flights))


# 2. Find the cheapest flight overall
cheapest = min(flights, key=lambda flight: flight["price"])

print("\nCheapest Flight:")
print(cheapest)


# 3. Find cities with no outgoing flights
all_cities = {flight["from"] for flight in flights} | \
             {flight["to"] for flight in flights}

departure_cities = {flight["from"] for flight in flights}

no_departures = all_cities - departure_cities

print("\nCities with no outgoing flights:")
print(no_departures)