import argparse
import configparser
from pathlib import Path

from .agent import ChatAgent
from .toolset import ExecuteShellCommandTool


def main():
    parser = argparse.ArgumentParser(description="Chat Agent Configuration")
    parser.add_argument(
        "--config",
        type=str,
        default="%s/.config/ai-shell-assistant/config.ini" % Path.home(),
        help="Path to the configuration file (default: ~/.config/ai-shell-assistant/config.ini)",
    )
    parser.add_argument(
        "--shortcuts",
        type=str,
        default="%s/.config/ai-shell-assistant/shortcuts" % Path.home(),
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

    tools = [ExecuteShellCommandTool()]
    chat_agent = ChatAgent(agent_config, tools)
    chat_agent.start_chat(prompt_config, args.shortcuts)


if __name__ == "__main__":
    main()
