import pathlib
import argparse
import configparser
import logging
import base64
import mimetypes
from .agent import ChatAgent


def read_file_content(file_path: pathlib.Path) -> str:
    mime, _ = mimetypes.guess_type(file_path)
    try:
        if mime and mime.startswith("image/"):
            with open(file_path, "rb") as f:
                encoded = base64.b64encode(f.read()).decode("utf-8")
            return f"[IMAGE:{file_path.name}:{mime}:base64]{encoded}"
        with open(file_path, "r", encoding="utf-8") as f:
            return f"[FILE:{file_path.name}]\n{f.read()}"
    except Exception as e:
        logging.error(f"Error reading file {file_path}: {e}")
        return f"[FILE:{file_path.name}] <COULD NOT READ>"


def read_dir_content(dir_path: pathlib.Path) -> str:
    return "\n\n".join(
        read_file_content(p)
        for p in dir_path.rglob("*")
        if p.is_file()
    )


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
        default=pathlib.Path.home() / ".config/ai-shell-assistant/config.ini"
    )
    parser.add_argument(
        "--shortcuts",
        type=pathlib.Path,
        default=pathlib.Path.home() / ".config/ai-shell-assistant/shortcuts"
    )
    parser.add_argument("--prompt", type=str, default=None)
    parser.add_argument(
        "--context",
        type=pathlib.Path,
        default=None,
        help="Archivo o directorio a cargar en el contexto del asistente"
    )
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

    extra_context = ""
    if args.context:
        if args.context.exists():
            if args.context.is_file():
                extra_context = read_file_content(args.context)
            elif args.context.is_dir():
                extra_context = read_dir_content(args.context)
            else:
                logging.error(f"Context path is neither a file nor a directory: {args.context}")
                return
        else:
            logging.error(f"Context file or directory not found: {args.context}")
            return

    prompt_config = {
        "configurable": {
            "thread_id": "1",
            "language": config.get("PREFERENCES", "language", fallback="English"),
            "so": config.get("PREFERENCES", "so", fallback="Linux"),
            "extra_context": extra_context,
        }
    }

    chat_agent = ChatAgent(config)
    chat_agent.start_chat(
        prompt_config,
        str(args.shortcuts),
        prompt=args.prompt if args.prompt else None
    )
