"""
Command handlers - pure functions that take input and return text.
"""

import asyncio
from services import LMSClient


def _get_client():
    """Create LMS client from config."""
    from config import load_config
    config = load_config()
    return LMSClient(
        base_url=config.get("LMS_API_URL", "http://localhost:42002"),
        api_key=config.get("LMS_API_KEY", ""),
    )


def handle_start(command: str) -> str:
    return (
        "Welcome to the LMS Bot! 🤖\n\n"
        "You can ask me questions in plain English, or use these commands:\n"
        "/help - Show available commands\n"
        "/health - Check system status\n"
        "/labs - List available labs\n"
        "/scores <lab> - View scores for a lab\n\n"
        "Try asking: \"what labs are available?\" or \"show me scores for lab 4\""
    )


def handle_help(command: str) -> str:
    return (
        "Available commands:\n"
        "/start - Welcome message\n"
        "/help - This help message\n"
        "/health - System status\n"
        "/labs - List available labs\n"
        "/scores <lab> - View scores for a specific lab\n\n"
        "You can also ask questions in plain English!"
    )


async def handle_health_async(command: str) -> str:
    client = _get_client()
    try:
        result = await client.health_check()
        if result["healthy"]:
            return f"Backend is healthy. {result['item_count']} items available."
        else:
            return f"Backend error: {result['error']}. Check that the services are running."
    finally:
        await client.close()


def handle_health(command: str) -> str:
    return asyncio.run(handle_health_async(command))


async def handle_labs_async(command: str) -> str:
    client = _get_client()
    try:
        items = await client.get_items()
        labs = [item for item in items if item.get("type") == "lab"]
        if not labs:
            return "No labs available."
        result = ["Available labs:"]
        for lab in labs:
            title = lab.get("title", "Unknown")
            result.append(f"- {title}")
        return "\n".join(result)
    except Exception as e:
        return f"Backend error: {e}. Check that the services are running."
    finally:
        await client.close()


def handle_labs(command: str) -> str:
    return asyncio.run(handle_labs_async(command))


async def handle_scores_async(command: str) -> str:
    parts = command.split()
    if len(parts) < 2:
        return "Usage: /scores <lab-id>\nExample: /scores lab-04\n\nUse /labs to see available labs."
    
    lab_id = parts[1]
    client = _get_client()
    
    try:
        analytics = await client.get_analytics("pass-rates", lab=lab_id)
        if not analytics:
            return f"No scores found for lab: {lab_id}"
        
        result = [f"Pass rates for {lab_id}:"]
        
        if isinstance(analytics, list):
            for item in analytics:
                task_name = item.get("task", item.get("title", "Unknown"))
                pass_rate = item.get("pass_rate", item.get("passRate", 0))
                attempts = item.get("attempts", 0)
                result.append(f"- {task_name}: {pass_rate:.1f}% ({attempts} attempts)")
        elif isinstance(analytics, dict):
            tasks = analytics.get("tasks", analytics.get("data", []))
            if isinstance(tasks, list):
                for item in tasks:
                    task_name = item.get("task", item.get("title", "Unknown"))
                    pass_rate = item.get("pass_rate", item.get("passRate", 0))
                    attempts = item.get("attempts", 0)
                    result.append(f"- {task_name}: {pass_rate:.1f}% ({attempts} attempts)")
            else:
                return f"Scores for {lab_id}: {analytics}"
        else:
            return f"Scores for {lab_id}: {analytics}"
        
        return "\n".join(result)
    except Exception as e:
        return f"Backend error: {e}. Check that the services are running."
    finally:
        await client.close()


def handle_scores(command: str) -> str:
    return asyncio.run(handle_scores_async(command))


def handle_unknown(command: str) -> str:
    return f"Unknown command: {command}. Use /help to see available commands."


# Import intent router for plain text messages
from .intent_router import route_intent

__all__ = [
    "handle_start",
    "handle_help",
    "handle_health",
    "handle_labs",
    "handle_scores",
    "handle_unknown",
    "route_intent",
]
