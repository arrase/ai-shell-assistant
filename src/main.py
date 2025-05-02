import argparse
import configparser
from pathlib import Path

from agent import ChatAgent


def main():
    parser = argparse.ArgumentParser(description="Chat Agent Configuration")
    parser.add_argument(
        "--config",
        type=str,
        default="%s/.config/ai-shell-assistant/config.ini" % Path.home(),
        help="Path to the configuration file (default: ~/.config/ai-shell-assistant/config.ini)",
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
    chat_agent.start_chat(prompt_config)


if __name__ == "__main__":
    main()
