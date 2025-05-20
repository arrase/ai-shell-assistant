import pathlib
import argparse
import configparser
import logging

from .agent import ChatAgent


def main():
    parser = argparse.ArgumentParser(description="AI Shell Assistant Configuration")

    parser.add_argument(
        "--config",
        type=pathlib.Path,
        default=pathlib.Path.home() / ".config/ai-shell-assistant/config.ini",
        help="Path to the configuration file (default: ~/.config/ai-shell-assistant/config.ini)",
    )

    parser.add_argument(
        "--shortcuts",
        type=pathlib.Path,
        default=pathlib.Path.home() / ".config/ai-shell-assistant/shortcuts",
        help="Path to the shortcuts directory (default: ~/.config/ai-shell-assistant/shortcuts)",
    )

    parser.add_argument(
        "--prompt",
        type=str,
        default=None,
        help="Prompt para ejecutar una consulta directa (no interactivo)",
    )

    args = parser.parse_args()

    agent_config = configparser.ConfigParser()
    agent_config.read(args.config)

    logging_level = agent_config.get("PREFERENCES", "logging_level", fallback="INFO").upper()
    logging.basicConfig(level=getattr(logging, logging_level, logging.INFO))

    if not args.config.exists():
        logging.error(f"Configuration file not found: {args.config}")
        return

    if not args.shortcuts.exists():
        logging.error(f"Shortcuts directory not found: {args.shortcuts}")
        return

    prompt_config = {
        "configurable": {
            "thread_id": "1",
            "language": agent_config.get("PREFERENCES", "language", fallback="English"),
            "so": agent_config.get("PREFERENCES", "so", fallback="Linux"),
        }
    }

    chat_agent = ChatAgent(agent_config, logging_level)
    if args.prompt:
        # Ejecuta el agente con el prompt proporcionado y termina
        chat_agent.start_chat(prompt_config, str(args.shortcuts), prompt=args.prompt)
    else:
        # Modo interactivo por defecto
        chat_agent.start_chat(prompt_config, str(args.shortcuts))
