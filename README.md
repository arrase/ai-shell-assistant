# AI Shell Assistant

This project provides an AI-powered shell assistant that can execute shell commands and assist with software development tasks. It uses a conversational agent built with the `langgraph` and `langchain_google_vertexai` libraries.

## Features

- Interactive chat interface.
- Executes shell commands using a toolset.
- Configurable language model with adjustable temperature and retries.
- Rich text output using `rich` for better readability.

# Develop

```
cd src
python3 main.py --config ../config/config.ini
```

# To-Do List

Planned features and improvements for this project.

- [ ] **Implement Web Search Capability:** Integrate functionality allowing the agent to perform searches on the web to retrieve current information, supplementing its internal knowledge base. This will enhance the agent's ability to answer questions about recent events, find definitions, look up documentation, and access other online resources.
- [ ] **Develop Special Command Shortcuts (e.g., `debug> command`):** Introduce a mechanism for users to invoke specific, predefined actions or modes via special syntax. A key example is the `debug> command` pattern, which should:
    - Execute the specified command 
    - Capture the standard output and error streams from the command execution.
    - Analyze the captured output, providing a clear explanation of its meaning.
    - Identify potential issues or errors indicated by the output.
    - Suggest concrete solutions or troubleshooting steps for any identified problems.
- [ ] **Add Persistent Long-Term Memory:** Implement a system for storing and retrieving information across different sessions or executions. This persistent memory should allow the agent to:
    - "Remember" specific facts, preferences, or instructions provided by the user in previous interactions.
    - Utilize this stored information to inform future responses and actions.
    - Support explicit user commands to add, modify, or recall items from memory (e.g., "remember that I prefer X", "what did I tell you about Y?").
    The goal is to create a more personalized and context-aware user experience by enabling the agent to build a cumulative understanding over time.

