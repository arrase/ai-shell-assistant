import pathlib
import argparse
import configparser
import logging
import base64
import mimetypes

from .agent import ChatAgent

def read_file_content(file_path: pathlib.Path) -> str:
    """Reads the content of a file.

    If the file is an image, it base64 encodes the content and formats it
    as a specific string. Otherwise, it reads the file as plain text.
    Handles common file reading errors and logs them.

    Args:
        file_path: The path to the file to read.

    Returns:
        A string containing the file content, prefixed with metadata,
        or an error message string if reading fails.
    """
    mime, _ = mimetypes.guess_type(file_path)
    if mime and mime.startswith("image/"):
        # Mypy doesn't like file_path directly in open with pathlib.Path, so convert to str
        with open(str(file_path), "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")
        return f"[IMAGE:{file_path.name}:{mime}:base64]{encoded}"
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f"[FILE:{file_path.name}]\n{f.read()}"
    except FileNotFoundError:
        logging.error(f"File not found: {str(file_path)}")
        return f"[FILE:{file_path.name}] <FILE NOT FOUND>"
    except IOError as e:
        logging.error(f"IOError reading file {str(file_path)}: {e}")
        return f"[FILE:{file_path.name}] <IO ERROR>"
    except UnicodeDecodeError as e:
        logging.error(f"UnicodeDecodeError reading file {str(file_path)}: {e}")
        return f"[FILE:{file_path.name}] <UNICODE DECODE ERROR>"
    except Exception as e:
        logging.error(f"An unexpected error occurred while reading file {str(file_path)}: {e}")
        return f"[FILE:{file_path.name}] <COULD NOT READ>"

def read_dir_content(dir_path: pathlib.Path) -> str:
    """Recursively reads the content of all files in a directory.

    Args:
        dir_path: The path to the directory.

    Returns:
        A string containing the concatenated content of all files found,
        with each file's content processed by `read_file_content`.
    """
    return "\n\n".join(
        read_file_content(path)
        for path in dir_path.rglob("*")
        if path.is_file()
    )

def _load_configuration(config_path: pathlib.Path) -> configparser.ConfigParser:
    """Loads the application configuration from the given path.

    Args:
        config_path: The path to the configuration file (.ini format).

    Returns:
        A ConfigParser object loaded with the configuration. If the file
        is not found, an error is logged and an empty ConfigParser object
        is returned.
    """
    agent_config = configparser.ConfigParser()
    if not config_path.exists():
        logging.error(f"Configuration file not found: {config_path}")
        # Return an empty config; caller should check or handle appropriately
    else:
        try:
            agent_config.read(config_path)
        except configparser.Error as e:
            logging.error(f"Error parsing configuration file {config_path}: {e}")
            # Return an empty config on parsing error as well
    return agent_config

def main() -> None:
    """Main entry point for the AI Shell Assistant.

    Parses command-line arguments, loads configuration, sets up logging,
    initializes the ChatAgent, and starts the chat session (either
    interactively or with a direct prompt).
    """
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

    agent_config = _load_configuration(args.config)

    # Setup logging as early as possible, but after config is loaded for custom level
    # If config is empty or PREFERENCES section is missing, fallback to INFO
    logging_level_str = "INFO"
    if 'PREFERENCES' in agent_config and 'logging_level' in agent_config['PREFERENCES']:
        logging_level_str = agent_config['PREFERENCES']['logging_level'].upper()
    else:
        if not agent_config.sections(): # Config was empty (e.g. file not found)
            logging.warning("Configuration file was not found or is empty. Using default INFO logging level.")
        else: # Config loaded but specific setting missing
            logging.warning("logging_level not found in PREFERENCES. Using default INFO logging level.")

    logging.basicConfig(level=getattr(logging, logging_level_str, logging.INFO))

    # Check if essential configuration is missing (e.g., if file wasn't found or was empty)
    # A more robust check might be to see if specific essential sections/keys exist.
    if not agent_config.sections():
        logging.error("Configuration is empty (file not found or unreadable). Assistant cannot start.")
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

    chat_agent = ChatAgent(agent_config)
    if args.prompt:
        chat_agent.start_chat(prompt_config, str(args.shortcuts), prompt=args.prompt)
    else:
        chat_agent.start_chat(prompt_config, str(args.shortcuts))
