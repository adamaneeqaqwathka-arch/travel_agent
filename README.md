# Agentic AI Travel Planning Assistant

An AI travel agent built with **LangChain** and **Google Gemini**. Given a request such as
*"Plan a 3-day trip from Bangalore to Goa"*, the agent decides for itself which tools to call
(flights, hotels, places, live weather, budget), reasons over the results and returns a
structured, day-wise itinerary with a cost breakdown and the reasoning behind its choices.

## Why this project
Planning a trip means switching between flight, hotel and attraction sites, comparing
inconsistent information and building an itinerary by hand. This assistant automates that
workflow in one place, the way travel platforms such as MakeMyTrip, Booking.com, Cleartrip
and Ixigo are moving toward conversational, agentic planning.

## Features
- **Autonomous tool use**: a tool-calling agent chooses which tools to call and in what order.
- **Flight search** with cheapest/fastest sorting and **one-stop connections** when no direct flight exists.
- **Hotel recommendations** filtered by city, minimum stars and maximum price.
- **Places discovery** by city, type and rating.
- **Live weather** from the free Open-Meteo API (no key needed).
- **Budget estimation**: flight + hotel x nights + daily food and local travel.
- **Structured output**: a validated Pydantic `Itinerary`, shown as readable text and as JSON.
- **Explanations**: the agent states why it chose each flight, hotel and place.
- **Two interfaces**: a Streamlit web app and a command-line script.

## Architecture
```
                 Streamlit UI (app.py)   /   CLI (main.py)
                              |
                              v
              Agent (agent/agent.py): LangChain + Gemini
              system prompt (agent/prompts.py)
                              |  tool calls
      +---------------+-------+--------+----------------+--------------+
      v               v                v                v              v
 flight_search   hotel_search    places_search     weather_tool     budget_tool
 (flights.json)  (hotels.json)   (places.json)     (Open-Meteo API) (arithmetic)
                              |
                              v
               Structured Itinerary (agent/schemas.py)
                              |
              readable text (agent/formatting.py) + JSON
```

## Project structure
```
travel_agent/
├── app.py                  Streamlit interface
├── main.py                 Command-line entry point
├── agent/
│   ├── agent.py            Builds and runs the Gemini tool-calling agent
│   ├── prompts.py          System prompt (workflow and rules)
│   ├── schemas.py          Pydantic models for the structured itinerary
│   ├── formatting.py       Itinerary -> readable text
│   └── tool_wrappers.py    LangChain @tool wrappers around the tools
├── tools/
│   ├── flights.py          Direct and one-stop flight search
│   ├── hotels.py           Hotel search
│   ├── places.py           Places search
│   ├── weather.py          Open-Meteo forecast lookup
│   └── budget.py           Trip cost estimation
├── data/raw/               flights.json, hotels.json, places.json
├── tests/                  Offline unit tests (pytest)
├── scripts/edge_cases.py   Hard queries to run against the live agent
├── requirements.txt
└── .env.example
```

## Setup
1. **Clone and enter the project**
   ```bash
   git clone <your-repo-url>
   cd travel_agent
   ```
2. **Create a virtual environment and install dependencies**
   ```bash
   python -m venv venv
   source venv/bin/activate        # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. **Add the datasets** to `data/raw/`: `flights.json`, `hotels.json`, `places.json`.
4. **Add your Gemini API key.** Get one free at <https://aistudio.google.com>, then:
   ```bash
   cp .env.example .env
   # edit .env and set GOOGLE_API_KEY=your_key
   ```
   Optionally set `GEMINI_MODEL` in `.env` to use a different Gemini model.

## Usage
**Web app**
```bash
streamlit run app.py
```
**Command line**
```bash
python main.py "Plan a 3 day trip from Bangalore to Goa starting in 3 days"
```
The CLI prints each tool call the agent makes, then the itinerary and its JSON.

## Example output
> Replace this section with a real run from your machine (text from the CLI or a
> screenshot of the app).

```
<paste a real itinerary here>
```

![Streamlit app screenshot](docs/app_screenshot.png)

## Testing
```bash
python -m pytest -q tests          # offline unit tests for all five tools
python -m scripts.edge_cases       # hard queries against the real agent (uses the API)
```
The unit tests need no API key or internet. `edge_cases.py` checks that the agent behaves
honestly in tricky situations: no route, too few places, missing place type, dates outside
the weather window, and missing information.

## Design decisions
- **Plain functions first, wrappers second.** Every tool is a normal Python function that
  is tested on its own; `tool_wrappers.py` only exposes it to the LLM.
- **Tools return errors as data.** An `{"error": ...}` result lets the agent explain the
  problem to the user instead of crashing the run.
- **Hotels are identified by `hotel_id`.** Hotel names are not unique in the dataset
  (for example two "Green Leaf Resort" entries in Goa).
- **Structured output via Pydantic.** The same object drives the text view, the UI and the
  JSON download.

## Data notes and limitations
- The datasets are small and synthetic: 30 flights, 40 hotels and 40 places across
  8 cities (Delhi, Mumbai, Goa, Bangalore, Chennai, Hyderabad, Kolkata, Jaipur).
- **Flights are sparse.** Only 25 routes exist and some pairs (for example Delhi to Goa)
  have no direct or one-stop connection; the agent reports this instead of inventing a flight.
- **Flight dates are all in 2025**, so flights are matched by route and treated as
  representative schedules; dates are not filtered. Prices are one-way.
- **One-stop connections** use the cheapest flight on each leg and ignore layover timing.
- **Place names and types are generic and partly random** (a "Park" may be typed as
  `fort`), so recommendations rely on `type` and `rating`.
- **Weather** is a live forecast, so trip dates must fall within about 15 days from today.
- Budget assumes a flat daily spend of Rs 800 for food and local travel.

## Possible improvements
- Use the Open-Meteo archive API to show typical weather for dates beyond the forecast window.
- Check layover times for connections and support return flights from real data.
- Add more cities and richer place data from a free API.

## Tech stack
Python, LangChain, Google Gemini (`langchain-google-genai`), Pydantic, Streamlit, Open-Meteo API, pytest.