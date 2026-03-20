"""
Command handlers — pure functions that take input and return text.

These handlers have no dependency on Telegram. They can be called from:
- --test mode (local testing)
- Unit tests
- Telegram bot (via the entry point)
"""


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
        "/scores — View your scores"
    )


def handle_health(command: str) -> str:
    """Handle /health command — reports system status."""
    return "Backend: unknown (not implemented yet)"


def handle_labs(command: str) -> str:
    """Handle /labs command — lists available labs."""
    return "Labs: not implemented yet"


def handle_scores(command: str) -> str:
    """Handle /scores command — shows scores."""
    return "Scores: not implemented yet"


def handle_unknown(command: str) -> str:
    """Handle unknown commands."""
    return f"Unknown command: {command}. Use /help to see available commands."
