import pathlib
import argparse
import configparser
import logging
from .agent import ChatAgent


def _load_configuration(config_path: pathlib.Path) -> configparser.ConfigParser:
    config = configparser.ConfigParser()
    if config_path.exists():
        try:
            config.read(config_path)
        except configparser.Error as e:
            logging.error(f"Error parsing configuration file {config_path}: {e}")
    else:
        logging.error(f"Configuration file not found: {config_path}")
    return config


def main() -> None:
    parser = argparse.ArgumentParser(description="AI Shell Assistant Configuration")
    parser.add_argument(
        "--config",
        type=pathlib.Path,
        default=pathlib.Path.home() / ".config/ai-shell-assistant/config.ini",
        help="Path to the configuration file"
    )
    parser.add_argument(
        "--shortcuts",
        type=pathlib.Path,
        default=pathlib.Path.home() / ".config/ai-shell-assistant/shortcuts",
        help="Directory containing shortcut files"
    )
    parser.add_argument("--prompt", type=str, default=None)
    args = parser.parse_args()

    config = _load_configuration(args.config)
    level = config.get("PREFERENCES", "logging_level", fallback="INFO").upper()
    logging.basicConfig(level=getattr(logging, level, logging.INFO))

    if not config.sections():
        logging.error("Configuration is empty (file not found or unreadable). Assistant cannot start.")
        return

    if not args.shortcuts.exists():
        logging.error(f"Shortcuts directory not found: {args.shortcuts}")
        return

    prompt_config = {
        "configurable": {
            "thread_id": "1",
            "language": config.get("PREFERENCES", "language", fallback="English"),
            "so": config.get("PREFERENCES", "so", fallback="Linux"),
        }
    }

    chat_agent = ChatAgent(config)
    chat_agent.start_chat(
        prompt_config,
        str(args.shortcuts),
        prompt=args.prompt if args.prompt else None
    )
