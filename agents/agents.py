"""Build and run the travel planning agent (LangChain tool-calling + Gemini)."""

import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI

from agent.prompts import build_system_prompt
from agent.tool_wrappers import ALL_TOOLS

DEFAULT_MODEL = "gemini-2.5-flash"


def build_agent():
    """Create the agent. Reads GOOGLE_API_KEY (and optional GEMINI_MODEL) from .env."""
    load_dotenv()
    if not os.getenv("GOOGLE_API_KEY"):
        raise RuntimeError("GOOGLE_API_KEY is missing. Add it to your .env file.")

    model = ChatGoogleGenerativeAI(
        model=os.getenv("GEMINI_MODEL", DEFAULT_MODEL),
        temperature=0,
    )
    return create_agent(model, ALL_TOOLS, system_prompt=build_system_prompt())


def plan_trip(query: str, verbose: bool = False) -> str:
    """Run the agent on a user query and return the final itinerary text."""
    agent = build_agent()
    result = agent.invoke({"messages": [{"role": "user", "content": query}]})

    if verbose:  # show the tool calls so you can watch the agent reason
        for message in result["messages"]:
            for call in getattr(message, "tool_calls", None) or []:
                print(f"[tool call] {call['name']}({call['args']})")

    content = result["messages"][-1].content
    if isinstance(content, list):  # some Gemini versions return content blocks
        content = "".join(
            block.get("text", "") if isinstance(block, dict) else str(block)
            for block in content
        )
    return content