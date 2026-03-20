"""
Command handlers — pure functions that take input and return text.

These handlers have no dependency on Telegram. They can be called from:
- --test mode (local testing)
- Unit tests
- Telegram bot (via the entry point)
"""

import asyncio
from typing import Optional
from services import LMSClient


def _get_client() -> LMSClient:
    """Create LMS client from config."""
    from config import load_config

    config = load_config()
    return LMSClient(
        base_url=config.get("LMS_API_URL", "http://localhost:42002"),
        api_key=config.get("LMS_API_KEY", ""),
    )


def handle_start(command: str) -> str:
    """Handle /start command — returns welcome message."""
    return "Welcome to the LMS Bot! Use /help to see available commands."


def handle_help(command: str) -> str:
    """Handle /help command — lists available commands."""
    return (
        "Available commands:\n"
        "/start — Welcome message\n"
        "/help — This help message\n"
        "/health — System status\n"
        "/labs — List available labs\n"
        "/scores <lab> — View scores for a specific lab"
    )


async def handle_health_async(command: str) -> str:
    """Handle /health command — reports system status."""
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
    """Handle /health command (sync wrapper)."""
    return asyncio.run(handle_health_async(command))


async def handle_labs_async(command: str) -> str:
    """Handle /labs command — lists available labs."""
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
    """Handle /labs command (sync wrapper)."""
    return asyncio.run(handle_labs_async(command))


async def handle_scores_async(command: str) -> str:
    """Handle /scores command — shows scores for a specific lab."""
    # Parse lab argument from command
    parts = command.split()
    if len(parts) < 2:
        return "Usage: /scores <lab-id>\nExample: /scores lab-04\n\nUse /labs to see available labs."

    lab_id = parts[1]

    client = _get_client()
    try:
        # Fetch pass rates for the lab
        analytics = await client.get_analytics("pass-rates", lab=lab_id)

        if not analytics:
            return f"No scores found for lab: {lab_id}"

        # Format the response
        result = [f"Pass rates for {lab_id}:"]

        # The analytics response should contain task data
        # Format depends on backend response structure
        if isinstance(analytics, list):
            for item in analytics:
                task_name = item.get("task", item.get("title", "Unknown"))
                pass_rate = item.get("pass_rate", item.get("passRate", 0))
                attempts = item.get("attempts", 0)
                result.append(f"- {task_name}: {pass_rate:.1f}% ({attempts} attempts)")
        elif isinstance(analytics, dict):
            # If it's a dict, try to extract tasks
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
    """Handle /scores command (sync wrapper)."""
    return asyncio.run(handle_scores_async(command))


def handle_unknown(command: str) -> str:
    """Handle unknown commands."""
    return f"Unknown command: {command}. Use /help to see available commands."
