import shutil
import pathlib
import argparse
import configparser
import importlib.resources

from .agent import ChatAgent
from .toolset import ExecuteShellCommandTool


def setup_user_config():
    """
    Checks if user config exists, creates it, and copies defaults if needed.
    """
    user_config_dir = pathlib.Path.home() / ".config" / "ai-shell-assistant"

    if not user_config_dir.exists():
        print(f"Creating configuration directory at: {user_config_dir}")
        user_config_dir.mkdir(parents=True, exist_ok=True)

        try:
            package_config_path_ref = importlib.resources.files(
                'ai_shell_assistant') / 'config'

            with importlib.resources.as_file(package_config_path_ref) as package_config_path:
                if package_config_path.is_dir():
                    print(
                        f"Copying default configuration from {package_config_path}...")
                    for item in package_config_path.iterdir():
                        destination_item = user_config_dir / item.name
                        if item.is_dir():
                            shutil.copytree(item, destination_item)
                        else:
                            shutil.copy2(item, destination_item)
                    print("Configuration copied.")
                else:
                    print(
                        f"Warning: 'config' directory not found inside the package at {package_config_path}")
        except ModuleNotFoundError:
            print(
                "Error: Could not find the 'ai_shell_assistant' package. Ensure it is installed.")
        except Exception as e:
            print(f"Error copying default configuration: {e}")
    else:
        print(f"Configuration directory already exists at: {user_config_dir}")


def main():
    setup_user_config()
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

    tools = [ExecuteShellCommandTool()]
    chat_agent = ChatAgent(agent_config, tools)
    chat_agent.start_chat(prompt_config, args.shortcuts)


if __name__ == "__main__":
    main()
