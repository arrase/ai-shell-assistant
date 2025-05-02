import os

import toolset

from langgraph.prebuilt import create_react_agent
from langchain_google_vertexai import ChatVertexAI
from langgraph.checkpoint.memory import InMemorySaver
from rich.console import Console
from rich.markdown import Markdown
from dotenv import load_dotenv


def main():
    load_dotenv()

    console = Console()

    system_prompt = "You are an expert Linux system administrator and software development assistant."

    llm = ChatVertexAI(
        model=os.getenv("GOOGLE_MODEL", "gemini-2.5-flash-preview-04-17"),
        temperature=os.getenv("TEMPERATURE", 0),
        max_tokens=None,
        max_retries=2,
    )

    agent = create_react_agent(
        model=llm,
        tools=[toolset.ExecuteLinuxCommandTool()],
        prompt=system_prompt,
        checkpointer=InMemorySaver(),
    )

    print("ChatBot initialized. Type 'quit', 'exit', or 'q' to end the conversation.")

    while True:
        try:
            user_input = input("~> ").strip()
            if user_input.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break
            if user_input:
                response = agent.invoke(
                    {"messages": [{"role": "user", "content": user_input},]},
                    {"configurable": {"thread_id": "1"}}
                )
                console.print(Markdown(response.get("messages")[-1].content))
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            break


if __name__ == "__main__":
    main()
