import readline  # Add edditline support for Unix-like systems
import logging

from langgraph.prebuilt import create_react_agent
from langchain_google_vertexai import ChatVertexAI
from langchain_community.chat_models import ChatOllama
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.runnables import RunnableConfig
from langgraph.prebuilt.chat_agent_executor import AgentState
from langchain_core.messages import AnyMessage
from rich.console import Console
from rich.markdown import Markdown
from langchain_community.tools import ShellTool
from langchain_community.tools import DuckDuckGoSearchRun

from .shortcuts import Shortcuts


class ChatAgent:
    def __init__(self, config, logging_level="INFO"):
        self.__console = Console()

        logging.basicConfig(level=getattr(
            logging, logging_level.upper(), logging.INFO))

        self.__agent = create_react_agent(
            model=self.__get_llm(config),
            tools=[ShellTool(), DuckDuckGoSearchRun()],
            prompt=self.__system_prompt,
            checkpointer=InMemorySaver(),
        )

    def start_chat(self, config, shortcuts_dir):
        # Load shortcuts
        shc = Shortcuts(shortcuts_dir)
        print("ChatBot initialized. Type 'quit', 'exit', or 'q' to end the conversation.")

        while True:
            try:
                user_input = input("~> ").strip()
                if user_input.lower() in ["quit", "exit", "q"]:
                    print("Goodbye!")
                    break
                # Replace user input with shortcut if it starts with '@'
                if user_input.startswith("@"):
                    prompt = shc.get_prompt(user_input)
                    if prompt:
                        user_input = prompt
                # Call the agent with the user input
                response = self.__agent.invoke(
                    {"messages": [
                        {"role": "user", "content": user_input}]},
                    config=config,
                )
                self.__console.print("\n")
                self.__console.print(
                    Markdown(response.get("messages")[-1].content))
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                logging.error(f"An unexpected error occurred: {e}")
                break

    def __get_llm(self, config):
        mode = config.get("PREFERENCES", "mode")
        model = config.get("MODEL", "name")
        temperature = config.get("MODEL", "temperature", fallback=0.0)
        max_retries = config.get("MODEL", "max_retries", fallback=2)

        if mode == "ollama":
            return ChatOllama(
                model=model,
                temperature=temperature,
                max_tokens=None,
                max_retries=max_retries,
            )
        elif mode == "vertex":
            return ChatVertexAI(
                model=model,
                temperature=temperature,
                max_tokens=None,
                max_retries=max_retries,
                project=config.get("VERTEX", "project"),
            )
        else:
            raise ValueError("Unsupported LLM mode specified.")

    def __system_prompt(self, state: AgentState, config: RunnableConfig) -> list[AnyMessage]:
        language = config["configurable"].get("language")
        so = config["configurable"].get("so")

        system_prompt = [
            f"You are an expert {so} system administrator and software development assistant.",
            f"You must respond to the user in {language}."
        ]

        return [{"role": "system", "content": "\n".join(system_prompt)}] + state["messages"]
