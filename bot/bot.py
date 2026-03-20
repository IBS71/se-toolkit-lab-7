"""
Telegram bot for LMS — Entry point

Usage:
    uv run bot.py --test "/start"   # Test a command locally
    uv run bot.py                   # Run the actual Telegram bot
"""

import argparse
import sys
from pathlib import Path

# Add the bot directory to the path so we can import handlers
bot_dir = Path(__file__).parent
sys.path.insert(0, str(bot_dir))

from handlers import (
    handle_start,
    handle_help,
    handle_health,
    handle_labs,
    handle_scores,
    handle_unknown,
)


def get_handler_for_command(command: str):
    """Route command to the appropriate handler."""
    # Extract just the command part (ignore arguments for routing)
    cmd = command.split()[0] if command.split() else command

    handlers = {
        "/start": handle_start,
        "/help": handle_help,
        "/health": handle_health,
        "/labs": handle_labs,
        "/scores": handle_scores,
    }
    return handlers.get(cmd, handle_unknown)


def run_test_mode(command: str):
    """Run a command in test mode — prints response to stdout."""
    handler = get_handler_for_command(command)
    response = handler(command)
    print(response)


def run_bot_mode():
    """Run the actual Telegram bot — to be implemented."""
    print("Starting Telegram bot... (not implemented yet)")
    print("To test commands, use: uv run bot.py --test '/start'")


def main():
    parser = argparse.ArgumentParser(description="LMS Telegram Bot")
    parser.add_argument(
        "--test",
        type=str,
        metavar="COMMAND",
        help="Test a command locally (e.g., --test '/start')",
    )
    args = parser.parse_args()

    if args.test:
        run_test_mode(args.test)
    else:
        run_bot_mode()


if __name__ == "__main__":
    main()
