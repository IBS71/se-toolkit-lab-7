"""
Telegram bot for LMS - Entry point

Usage:
    uv run bot.py --test "/start"   # Test a command locally
    uv run bot.py --test "hello"    # Test natural language
    uv run bot.py                   # Run the actual Telegram bot
"""

import argparse
import sys
from pathlib import Path

bot_dir = Path(__file__).parent
sys.path.insert(0, str(bot_dir))

from handlers import (
    handle_start,
    handle_help,
    handle_health,
    handle_labs,
    handle_scores,
    handle_unknown,
    route_intent,
)


def get_handler_for_command(command: str):
    """Route command to the appropriate handler."""
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
    """Run a command in test mode - prints response to stdout."""
    # Check if it's a slash command or plain text
    if command.startswith("/"):
        handler = get_handler_for_command(command)
        response = handler(command)
    else:
        # Plain text - route to LLM
        response = route_intent(command)
    
    print(response)


def run_bot_mode():
    """Run the actual Telegram bot - to be implemented."""
    print("Starting Telegram bot... (not implemented yet)")
    print("To test commands, use: uv run bot.py --test '/start'")
    print("To test natural language, use: uv run bot.py --test 'hello'")


def main():
    parser = argparse.ArgumentParser(description="LMS Telegram Bot")
    parser.add_argument(
        "--test",
        type=str,
        metavar="MESSAGE",
        help="Test a command or message locally (e.g., --test '/start' or --test 'hello')",
    )
    args = parser.parse_args()

    if args.test:
        run_test_mode(args.test)
    else:
        run_bot_mode()


if __name__ == "__main__":
    main()
