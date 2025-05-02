from langgraph.prebuilt import create_react_agent
from langchain_google_vertexai import ChatVertexAI
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.runnables import RunnableConfig
from langgraph.prebuilt.chat_agent_executor import AgentState
from langchain_core.messages import AnyMessage
from rich.console import Console
from rich.markdown import Markdown

import toolset


class ChatAgent:
    def __init__(self, config):
        self.__console = Console()

        llm = ChatVertexAI(
            model=config.get("MODEL", "name"),
            temperature=config.get("MODEL", "temperature", fallback=0.0),
            max_tokens=None,
            max_retries=config.get("MODEL", "max_retries", fallback=2),
            project=config.get("VERTEX", "project"),
        )

        self.__agent = create_react_agent(
            model=llm,
            tools=[toolset.ExecuteShellCommandTool()],
            prompt=self.__system_prompt,
            checkpointer=InMemorySaver(),
        )

    def start_chat(self, config):
        print("ChatBot initialized. Type 'quit', 'exit', or 'q' to end the conversation.")

        while True:
            try:
                user_input = input("~> ").strip()
                if user_input.lower() in ["quit", "exit", "q"]:
                    print("Goodbye!")
                    break
                if user_input:
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
                print(f"An unexpected error occurred: {e}")
                break

    def __system_prompt(self, state: AgentState, config: RunnableConfig) -> list[AnyMessage]:
        language = config["configurable"].get("language")
        so = config["configurable"].get("so")

        system_msg = f"""
        You are an expert {so} system administrator and software development assistant.
        You must respond to the user in {language}.
        """
        return [{"role": "system", "content": system_msg}] + state["messages"]
