import argparse
import configparser

import toolset

from langgraph.prebuilt import create_react_agent
from langchain_google_vertexai import ChatVertexAI
from langgraph.checkpoint.memory import InMemorySaver
from rich.console import Console
from rich.markdown import Markdown


class ChatAgent:
    def __init__(self, system_prompt, model_name, temperature, max_retries):
        self.console = Console()
        self.system_prompt = system_prompt

        llm = ChatVertexAI(
            model=model_name,
            temperature=temperature,
            max_tokens=None,
            max_retries=max_retries,
        )

        self.agent = create_react_agent(
            model=llm,
            tools=[toolset.ExecuteLinuxCommandTool()],
            prompt=self.system_prompt,
            checkpointer=InMemorySaver(),
        )

    def start_chat(self):
        print("ChatBot initialized. Type 'quit', 'exit', or 'q' to end the conversation.")

        while True:
            try:
                user_input = input("~> ").strip()
                if user_input.lower() in ["quit", "exit", "q"]:
                    print("Goodbye!")
                    break
                if user_input:
                    response = self.agent.invoke(
                        {"messages": [
                            {"role": "user", "content": user_input}]},
                        {"configurable": {"thread_id": "1"}},
                    )
                    self.console.print("\n")
                    self.console.print(
                        Markdown(response.get("messages")[-1].content))
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                break


def main():
    parser = argparse.ArgumentParser(description="Chat Agent Configuration")
    parser.add_argument(
        "--config",
        type=str,
        default="config.ini",
        help="Path to the configuration file (default: ./config.ini)",
    )
    args = parser.parse_args()

    config = configparser.ConfigParser()
    config.read(args.config)

    system_prompt = "You are an expert Linux system administrator and software development assistant."
    model_name = config.get("MODEL", "name")
    temperature = float(config.get("MODEL", "temperature", fallback=0.0))
    max_retries = 2

    chat_agent = ChatAgent(system_prompt, model_name, temperature, max_retries)
    chat_agent.start_chat()


if __name__ == "__main__":
    main()
