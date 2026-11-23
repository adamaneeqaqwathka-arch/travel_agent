"""Offline tests for the plain Python tools (no LLM, no network)."""

from datetime import date, timedelta
from unittest import mock

import pytest

from tools.budget import estimate_budget
from tools.flights import find_flight_options, search_flights
from tools.hotels import search_hotels
from tools.places import search_places
from tools.weather import get_weather


# ---------- flights ----------
def test_direct_flight_found():
    result = find_flight_options("Mumbai", "Goa")
    assert result["type"] == "direct"
    assert all(f["from"] == "Mumbai" and f["to"] == "Goa" for f in result["options"])


def test_flight_search_is_case_insensitive_and_sorted_by_price():
    flights = search_flights("goa", "bangalore", "price")
    prices = [f["price"] for f in flights]
    assert prices == sorted(prices) and len(prices) >= 1


def test_one_stop_connection_when_no_direct_flight():
    result = find_flight_options("Bangalore", "Hyderabad")
    assert result["type"] == "one_stop"
    totals = [o["total_price"] for o in result["options"]]
    assert totals == sorted(totals)
    for option in result["options"]:
        assert option["legs"][0]["to"] == option["legs"][1]["from"]


def test_no_route_returns_none_with_message():
    result = find_flight_options("Delhi", "Goa")
    assert result["type"] == "none"
    assert "Delhi" in result["message"]


def test_invalid_sort_raises():
    with pytest.raises(ValueError):
        search_flights("Goa", "Mumbai", "banana")


# ---------- hotels ----------
def test_hotels_filtered_by_stars_and_price():
    hotels = search_hotels("Goa", min_stars=4, max_price=4000)
    assert all(h["stars"] >= 4 and h["price_per_night"] <= 4000 for h in hotels)


def test_hotels_sorted_by_stars_then_price():
    hotels = search_hotels("Goa")
    keys = [(-h["stars"], h["price_per_night"]) for h in hotels]
    assert keys == sorted(keys)


def test_unknown_city_has_no_hotels():
    assert search_hotels("Atlantis") == []


def test_hotels_have_unique_ids():
    ids = [h["hotel_id"] for city in ("Goa", "Delhi", "Mumbai") for h in search_hotels(city)]
    assert len(ids) == len(set(ids))


def test_zero_max_price_is_a_real_limit():
    assert search_hotels("Goa", max_price=0) == []


# ---------- places ----------
def test_places_sorted_by_rating_and_limited():
    places = search_places("Goa", limit=2)
    assert len(places) == 2
    assert places[0]["rating"] >= places[1]["rating"]


def test_places_type_filter_may_be_empty():
    for place in search_places("Goa", place_type="beach"):
        assert place["type"] == "beach"


# ---------- budget ----------
def test_budget_matches_brief_example():
    result = estimate_budget(4800, 3200, 3)
    assert result["hotel"] == 6400 and result["nights"] == 2
    assert result["total"] == 4800 + 6400 + 3 * 800


@pytest.mark.parametrize("args", [(4800, 3200, 0), (-1, 3200, 3), (4800, -5, 3)])
def test_budget_rejects_bad_input(args):
    assert "error" in estimate_budget(*args)


def test_one_day_trip_has_no_hotel_cost():
    assert estimate_budget(1000, 5000, 1)["hotel"] == 0


# ---------- weather (network mocked) ----------
def _fake_response(start):
    response = mock.Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = {"daily": {
        "time": [start.isoformat()],
        "temperature_2m_max": [31.0],
        "temperature_2m_min": [24.0],
        "weathercode": [2],
    }}
    return response


def test_weather_reshapes_api_response():
    today = date.today()
    with mock.patch("tools.weather.requests.get", return_value=_fake_response(today)):
        result = get_weather("Goa", today.isoformat(), today.isoformat())
    assert result["days"][0]["condition"] == "Partly cloudy"
    assert result["days"][0]["max_temp_c"] == 31.0


def test_weather_unknown_city():
    assert "error" in get_weather("Atlantis", "2030-01-01", "2030-01-02")


def test_weather_dates_outside_window():
    far = (date.today() + timedelta(days=60)).isoformat()
    assert "error" in get_weather("Goa", far, far)


def test_weather_bad_date_format():
    assert "error" in get_weather("Goa", "tomorrow", "later")


def test_weather_network_failure_returns_error():
    import requests
    today = date.today().isoformat()
    with mock.patch("tools.weather.requests.get", side_effect=requests.ConnectionError("offline")):
        assert "error" in get_weather("Goa", today, today)