"""
Configuration loader — reads secrets from .env.bot.secret

Usage:
    from config import load_config
    config = load_config()
    print(config["BOT_TOKEN"])
"""

from pathlib import Path
from dotenv import dotenv_values


def load_config() -> dict:
    """Load configuration from .env.bot.secret file."""
    # Find the .env.bot.secret file in the same directory as this script
    base_dir = Path(__file__).parent
    env_file = base_dir / ".env.bot.secret"

    if not env_file.exists():
        # Fall back to .env.bot.example if secret doesn't exist
        env_file = base_dir / ".env.bot.example"

    config = dotenv_values(env_file)

    # Validate required fields
    required = ["BOT_TOKEN", "LMS_API_URL", "LMS_API_KEY"]
    missing = [key for key in required if not config.get(key)]

    if missing:
        print(f"Warning: Missing config values: {missing}")
        print(f"Make sure {env_file} has all required fields")

    return config
