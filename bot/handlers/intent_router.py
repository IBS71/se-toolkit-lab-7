"""
Intent Router - Routes natural language messages to LLM with tools.

Usage:
    from handlers import route_intent
    response = route_intent("which lab has the lowest pass rate?")
"""

import asyncio
import sys
from config import load_config
from services import LLMClient, TOOLS


# System prompt for the LLM
SYSTEM_PROMPT = """You are a helpful assistant for a Learning Management System (LMS). 
You have access to tools that let you fetch data about labs, tasks, learners, and analytics.

When a user asks a question:
1. Think about what data they need
2. Call the appropriate tool(s) to get that data
3. Use the tool results to formulate a helpful answer

Available tools:
- get_items: List all labs and tasks
- get_learners: List enrolled students
- get_scores: Get score distribution for a lab
- get_pass_rates: Get pass rates per task for a lab
- get_timeline: Get submission timeline for a lab
- get_groups: Get per-group performance for a lab
- get_top_learners: Get top N learners for a lab
- get_completion_rate: Get completion rate for a lab
- trigger_sync: Refresh data from autochecker

For greetings like "hello" or "hi", respond friendly and mention what you can help with.
For unclear messages, politely ask for clarification and suggest what you can do.

Always be specific and include numbers when available. Format your answers clearly."""


async def route_intent_async(message: str) -> str:
    """
    Route a natural language message to the LLM.

    Args:
        message: User's message in plain text

    Returns:
        Response from the LLM
    """
    config = load_config()

    llm = LLMClient(
        api_key=config.get("LLM_API_KEY", ""),
        base_url=config.get("LLM_API_BASE_URL", "http://localhost:42005/v1"),
        model=config.get("LLM_API_MODEL", "coder-model"),
    )

    try:
        # Build conversation with system prompt
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message},
        ]

        # Call LLM with tools
        response = await llm.chat_with_tools(messages, TOOLS)
        return response

    except Exception as e:
        return f"LLM error: {e}. Please try again or use slash commands like /help."

    finally:
        await llm.close()


def route_intent(message: str) -> str:
    """Sync wrapper for route_intent_async."""
    return asyncio.run(route_intent_async(message))


# Keyboard buttons for common actions
KEYBOARD_BUTTONS = [
    ["📚 List Labs", "🏥 Health Check"],
    ["📊 My Scores", "👥 Top Learners"],
    ["❓ Help", "🔄 Refresh Data"],
]


def get_keyboard_markup() -> str:
    """Get inline keyboard markup as text description."""
    return "Keyboard: " + " | ".join(
        [btn for row in KEYBOARD_BUTTONS for btn in row]
    )
