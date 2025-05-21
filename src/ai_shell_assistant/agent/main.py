import readline
import logging
import sys
import configparser
from typing import Any, Dict, Optional, List, Union, Type

from langgraph.prebuilt import create_react_agent
from langchain_google_vertexai import ChatVertexAI
from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.runnables import RunnableConfig
from langgraph.prebuilt.chat_agent_executor import AgentState
from langchain_core.messages import BaseMessage
from rich.console import Console
from rich.markdown import Markdown
from langchain_community.tools import ShellTool, DuckDuckGoSearchRun

from .shortcuts import Shortcuts


class ChatAgent:
    def __init__(self, config: configparser.ConfigParser) -> None:
        self.__console = Console()
        self.__agent = create_react_agent(
            model=self.__get_llm(config),
            tools=[ShellTool(), DuckDuckGoSearchRun()],
            prompt=self.__system_prompt,
            checkpointer=InMemorySaver(),
        )

    def __resolve_input(self, inp, shortcuts):
        return shortcuts.get_prompt(inp) if inp.startswith("@") else inp

    def start_chat(self, config: Dict[str, Any], shortcuts_dir: str, prompt: Optional[str] = None) -> None:
        shortcuts = Shortcuts(shortcuts_dir)

        if prompt is not None:
            user_input = self.__resolve_input(prompt.strip(), shortcuts)
            response = self.__agent.invoke(
                {"messages": [{"role": "user", "content": user_input}]}, config=config
            )
            self.__console.print("\n")
            self.__console.print(Markdown(response.get("messages")[-1].content))
            return

        print("ChatBot initialized. Type 'quit', 'exit' or 'q' to end the conversation.")
        while True:
            try:
                user_input = input("~> ").strip()
                if user_input.lower() in {"quit", "exit", "q"}:
                    print("Goodbye!")
                    break
                user_input = self.__resolve_input(user_input, shortcuts)
                response = self.__agent.invoke(
                    {"messages": [{"role": "user", "content": user_input}]}, config=config
                )
                self.__console.print("\n")
                self.__console.print(Markdown(response.get("messages")[-1].content))
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                logging.error(f"An unexpected error occurred: {e}")
                break

    def __get_llm(self, config: configparser.ConfigParser) -> Union[ChatOllama, ChatVertexAI, Type[ChatGoogleGenerativeAI]]:  # type: ignore
        try:
            mode = config.get("PREFERENCES", "mode")
            logging.info(f"Using LLM mode: {mode}")
        except Exception as e:
            logging.error(f"Missing 'mode' in '[PREFERENCES]': {e}")
            sys.exit(1)

        temperature = config.getfloat("MODEL", "temperature", fallback=0.0)
        max_retries = config.getint("MODEL", "max_retries", fallback=2)

        try:
            name = config.get("MODEL", "name")
        except Exception as e:
            logging.error(f"Missing model name: {e}")
            sys.exit(1)

        if mode == "ollama":
            return ChatOllama(
                model=name,
                temperature=temperature,
                max_tokens=None,
                max_retries=max_retries
            )
        elif mode == "vertex":
            try:
                project = config.get("VERTEX", "project")
            except Exception as e:
                logging.error(f"Missing Vertex config: {e}")
                sys.exit(1)
            return ChatVertexAI(
                model=name,
                temperature=temperature,
                max_tokens=None,
                max_retries=max_retries,
                project=project
            )
        elif mode == "aistudio":
            try:
                api_key = config.get("AISTUDIO", "google_api_key")
            except Exception as e:
                logging.error(f"Missing AI Studio config: {e}")
                sys.exit(1)
            return ChatGoogleGenerativeAI(
                model=name,
                google_api_key=api_key,
                temperature=temperature,
                max_retries=max_retries
            )
        else:
            logging.error(f"Unsupported LLM mode: '{mode}'.")
            sys.exit(1)

    def __system_prompt(self, state: AgentState, config: RunnableConfig) -> List[BaseMessage]:
        c = config["configurable"]
        language = c.get("language", "English")
        so = c.get("so", "Linux")
        extra = c.get("extra_context", "")

        prompt = (
            f"You are an expert {so} system administrator and software development assistant.\n"
            f"You must respond to the user in {language}."
        )
        if extra:
            prompt += f"\n\nThe following context is provided for this session:\n{extra}"

        messages: List[BaseMessage] = [
            {"role": "system", "content": prompt}
        ]
        messages.extend(state["messages"])
        return messages
