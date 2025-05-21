import readline  # Add edditline support for Unix-like systems
import logging
import sys
import configparser
from typing import Any, Dict, Optional, List, Union

from langgraph.prebuilt import create_react_agent
from langchain_google_vertexai import ChatVertexAI
from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import InMemorySaver # type: ignore
from langchain_core.runnables import RunnableConfig
from langgraph.prebuilt.chat_agent_executor import AgentState # type: ignore
from langchain_core.messages import AnyMessage, BaseMessage
from rich.console import Console
from rich.markdown import Markdown
from langchain_community.tools import ShellTool
from langchain_community.tools import DuckDuckGoSearchRun

from .shortcuts import Shortcuts


class ChatAgent:
    def __init__(self, config: configparser.ConfigParser) -> None:
        """Initializes the ChatAgent.

        Sets up the console and initializes the reactive agent with the specified
        LLM, tools, system prompt, and memory. Logging is expected to be
        configured globally before this class is instantiated.

        Args:
            config: Configuration object containing settings for the LLM and agent.
        """
        self.__console = Console()

        # Initialize the agent
        self.__agent = create_react_agent(
            model=self.__get_llm(config),
            tools=[ShellTool(), DuckDuckGoSearchRun()],
            prompt=self.__system_prompt, # type: ignore
            checkpointer=InMemorySaver(),
        )

    def start_chat(self, config: Dict[str, Any], shortcuts_dir: str, prompt: Optional[str] = None) -> None:
        """Starts the chat interaction with the user.

        Handles both interactive chat mode and non-interactive (single prompt) mode.
        Loads shortcuts, processes user input, invokes the agent, and displays responses.

        Args:
            config: Runtime configuration for the agent, including thread_id, language, etc.
            shortcuts_dir: Path to the directory containing shortcut definitions.
            prompt: An optional string. If provided, the agent executes this prompt
                    non-interactively and then exits. Otherwise, enters interactive mode.
        """
        # Load shortcuts
        shortcuts = Shortcuts(shortcuts_dir) # logging_level is not passed anymore
        if prompt is not None:
            user_input = prompt.strip()
            if user_input.startswith("@"):
                resolved = shortcuts.get_prompt(user_input)
                user_input = resolved if resolved else user_input
            response = self.__agent.invoke(
                {"messages": [{"role": "user", "content": user_input}]},
                config=config,
            )
            self.__console.print("\n")
            self.__console.print(
                Markdown(response.get("messages")[-1].content))
            return

        print("ChatBot initialized. Type 'quit', 'exit' or 'q' to end the conversation.")

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
                    user_input = prompt if prompt else user_input

                # Invoke the agent with the user's input
                response = self.__agent.invoke(
                    {"messages": [{"role": "user", "content": user_input}]},
                    config=config,
                )

                # Display the agent's response
                self.__console.print("\n")
                self.__console.print(
                    Markdown(response.get("messages")[-1].content))

            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                logging.error(f"An unexpected error occurred: {e}")
                break

    def __get_llm(self, config: configparser.ConfigParser) -> Union[ChatOllama, ChatVertexAI]:
        """Configures and returns the Language Model (LLM) based on settings.

        Supports 'ollama' and 'vertex' modes. Reads model name, temperature,
        and other parameters from the provided configuration.

        Args:
            config: The application's configuration object.

        Returns:
            An instance of ChatOllama or ChatVertexAI.

        Raises:
            SystemExit: If an unsupported LLM mode is specified.
        """
        # Retrieve LLM configuration
        mode = config.get("PREFERENCES", "mode")
        logging.info(f"Using LLM mode: {mode}")

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

    def __system_prompt(self, state: AgentState, config: RunnableConfig) -> List[BaseMessage]:
        """Constructs the system prompt for the agent.

        Incorporates language preference, operating system context, and any
        additional context provided in the configuration. It then prepends this
        system message to the current conversation history.

        Args:
            state: The current state of the agent, containing message history.
            config: The runnable configuration, containing language, OS, and extra context.

        Returns:
            A list of messages, starting with the generated system prompt,
            followed by the existing messages from the state.
        """
        # Retrieve language and system information from the configuration
        language: str = config["configurable"].get("language", "English")
        so: str = config["configurable"].get("so", "Linux")
        extra_context = config["configurable"].get("extra_context", "")

        # Build the system prompt using an f-string
        system_prompt_content = f"You are an expert {so} system administrator and software development assistant.\n"
        system_prompt_content += f"You must respond to the user in {language}."

        if extra_context:
            system_prompt_content += f"\n\nThe following context is provided for this session:\n{extra_context}"

        # Return the system prompt along with the current state messages
        messages: List[BaseMessage] = [{"role": "system", "content": system_prompt_content}] # type: ignore
        messages.extend(state["messages"])
        return messages
