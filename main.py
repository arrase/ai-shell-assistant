import os

import toolset

from langgraph.prebuilt import create_react_agent
from langchain_google_vertexai import ChatVertexAI
from langgraph.checkpoint.memory import InMemorySaver
from dotenv import load_dotenv

load_dotenv()


system_prompt = "You are an expert Linux system administrator and software development assistant."


llm = ChatVertexAI(
    model=os.getenv("GOOGLE_MODEL"),
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


def main():
    print("ChatBot initialized. Type 'quit', 'exit', or 'q' to end the conversation.")

    while True:
        try:
            user_input = input("User: ").strip()
            if user_input.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break
            if user_input:
                response = agent.invoke(
                    {"messages": [{"role": "user", "content": user_input},]},
                    {"configurable": {"thread_id": "1"}}
                )
                print(response.get("messages")[-1].content)
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            break


if __name__ == "__main__":
    main()
