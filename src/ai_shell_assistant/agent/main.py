import readline  # Add edditline support for Unix-like systems
import logging
import sys

from langgraph.prebuilt import create_react_agent
from langchain_google_vertexai import ChatVertexAI
from langchain_ollama import ChatOllama
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

        # Configure logging
        logging.basicConfig(
            level=getattr(logging, logging_level.upper(), logging.INFO)
        )

        # Initialize the agent
        self.__agent = create_react_agent(
            model=self.__get_llm(config),
            tools=[ShellTool(), DuckDuckGoSearchRun()],
            prompt=self.__system_prompt,
            checkpointer=InMemorySaver(),
        )

    def start_chat(self, config, shortcuts_dir):
        # Load shortcuts
        shortcuts = Shortcuts(shortcuts_dir)
        print("ChatBot initialized. Type 'quit', 'exit', or 'q' to end the conversation.")

        while True:
            try:
                user_input = input("~> ").strip()

                # Exit the chat
                if user_input.lower() in {"quit", "exit", "q"}:
                    print("Goodbye!")
                    break

                # Replace user input with a shortcut if it starts with '@'
                if user_input.startswith("@"):
                    prompt = shortcuts.get_prompt(user_input)
                    if prompt:
                        user_input = prompt

                # Invoke the agent with the user's input
                response = self.__agent.invoke(
                    {"messages": [{"role": "user", "content": user_input}]},
                    config=config,
                )

                # Display the agent's response
                self.__console.print("\n")
                self.__console.print(Markdown(response.get("messages")[-1].content))

            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                logging.error(f"An unexpected error occurred: {e}")
                break

    def __get_llm(self, config):
        # Retrieve LLM configuration
        mode = config.get("PREFERENCES", "mode")
        print(f"Using LLM mode: {mode}")

        model = config.get("MODEL", "name")
        temperature = config.getfloat("MODEL", "temperature", fallback=0.0)
        max_retries = config.getint("MODEL", "max_retries", fallback=2)

        # Initialize the appropriate LLM based on the mode
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
            # Handle unsupported LLM mode
            logging.error(f"Error: Unsupported LLM mode specified: {mode}")
            sys.exit(1)  # Terminate the program

    def __system_prompt(self, state: AgentState, config: RunnableConfig) -> list[AnyMessage]:
        # Retrieve language and system information from the configuration
        language = config["configurable"].get("language", "English")
        so = config["configurable"].get("so", "Linux")

        # Build the system prompt
        system_prompt = [
            f"You are an expert {so} system administrator and software development assistant.",
            f"You must respond to the user in {language}."
        ]

        # Return the system prompt along with the current state messages
        return [{"role": "system", "content": "\n".join(system_prompt)}] + state["messages"]
