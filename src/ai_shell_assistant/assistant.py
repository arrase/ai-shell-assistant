import pathlib
import argparse
import configparser

from .agent import ChatAgent


def main():
    parser = argparse.ArgumentParser(description="Chat Agent Configuration")
    parser.add_argument(
        "--config",
        type=str,
        default="%s/.config/ai-shell-assistant/config.ini" % pathlib.Path.home(),
        help="Path to the configuration file (default: ~/.config/ai-shell-assistant/config.ini)",
    )
    parser.add_argument(
        "--shortcuts",
        type=str,
        default="%s/.config/ai-shell-assistant/shortcuts" % pathlib.Path.home(),
        help="Path to the shortcuts directory (default: ~/.config/ai-shell-assistant/shortcuts)",
    )
    args = parser.parse_args()

    agent_config = configparser.ConfigParser()
    agent_config.read(args.config)

    prompt_config = {"configurable": {
        "thread_id": "1",
        "language": agent_config.get("PREFERENCES", "language"),
        "so": agent_config.get("PREFERENCES", "so"),
    }}

    chat_agent = ChatAgent(agent_config)
    chat_agent.start_chat(prompt_config, args.shortcuts)


if __name__ == "__main__":
    main()
