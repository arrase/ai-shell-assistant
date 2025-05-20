import pathlib
import argparse
import configparser
import logging
import base64
import mimetypes

from .agent import ChatAgent

def read_file_content(file_path):
    mime, _ = mimetypes.guess_type(file_path)
    if mime and mime.startswith("image/"):
        with open(file_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")
        return f"[IMAGE:{file_path.name}:{mime}:base64]{encoded}"
    else:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f"[FILE:{file_path.name}]\n{f.read()}"
        except Exception:
            return f"[FILE:{file_path.name}] <COULD NOT READ>"

def read_dir_content(dir_path):
    context = []
    for path in dir_path.rglob("*"):
        if path.is_file():
            context.append(read_file_content(path))
    return "\n\n".join(context)

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
        help="Prompt to execute a direct query (non-interactive)",
    )

    parser.add_argument(
        "--file",
        type=pathlib.Path,
        default=None,
        help="File to load into the agent's context",
    )

    parser.add_argument(
        "--dir",
        type=pathlib.Path,
        default=None,
        help="Directory to recursively load into the agent's context",
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

    extra_context = ""
    if args.file:
        if args.file.exists() and args.file.is_file():
            extra_context = read_file_content(args.file)
        else:
            logging.error(f"File not found: {args.file}")
            return
    elif args.dir:
        if args.dir.exists() and args.dir.is_dir():
            extra_context = read_dir_content(args.dir)
        else:
            logging.error(f"Directory not found: {args.dir}")
            return

    prompt_config = {
        "configurable": {
            "thread_id": "1",
            "language": agent_config.get("PREFERENCES", "language", fallback="English"),
            "so": agent_config.get("PREFERENCES", "so", fallback="Linux"),
            "extra_context": extra_context,
        }
    }

    chat_agent = ChatAgent(agent_config, logging_level)
    if args.prompt:
        # Run the agent with the provided prompt and exit
        chat_agent.start_chat(prompt_config, str(args.shortcuts), prompt=args.prompt)
    else:
        # Default interactive mode
        chat_agent.start_chat(prompt_config, str(args.shortcuts))
