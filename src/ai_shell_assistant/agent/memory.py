import json
import os
from typing import Type, Optional, Any
from langchain_core.tools import BaseTool
from pydantic.v1 import BaseModel, Field # Using pydantic.v1 for broader compatibility

DEFAULT_MEMORY_FILE = "config/agent_memory.json"

# Helper functions (mostly unchanged, but made private or kept for direct use if needed)

def initialize_memory_file(file_path: str = DEFAULT_MEMORY_FILE):
    """Ensures the memory file exists, creating an empty JSON object if not."""
    dir_name = os.path.dirname(file_path)
    if dir_name and not os.path.exists(dir_name):
        os.makedirs(dir_name, exist_ok=True)
    if not os.path.exists(file_path):
        with open(file_path, 'w') as f:
            json.dump({}, f)

def _read_memory(file_path: str = DEFAULT_MEMORY_FILE) -> dict:
    """Reads and parses JSON from the memory file."""
    initialize_memory_file(file_path)
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            if not content:
                return {}
            return json.loads(content)
    except (FileNotFoundError, json.JSONDecodeError):
        initialize_memory_file(file_path)
        return {}

def _write_memory(file_path: str, data: dict):
    """Writes JSON data to the memory file."""
    initialize_memory_file(file_path)
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

# Core memory operations

def _save_to_memory(key: str, value: any, file_path: str = DEFAULT_MEMORY_FILE) -> str:
    try:
        data = _read_memory(file_path)
        data[key] = value
        _write_memory(file_path, data)
        return f"Successfully saved {{ '{key}': '{value}' }} to memory."
    except Exception as e:
        return f"Error saving to memory: {e}"

def _retrieve_from_memory(key: str, file_path: str = DEFAULT_MEMORY_FILE) -> any:
    data = _read_memory(file_path)
    value = data.get(key)
    if value is not None:
        return value
    else:
        return f"Key '{key}' not found in memory."

def _delete_from_memory(key: str, file_path: str = DEFAULT_MEMORY_FILE) -> str:
    data = _read_memory(file_path)
    if key in data:
        del data[key]
        _write_memory(file_path, data)
        return f"Successfully deleted '{key}' from memory."
    return f"Key '{key}' not found in memory, nothing to delete."

def _get_all_memory(file_path: str = DEFAULT_MEMORY_FILE) -> dict:
    return _read_memory(file_path)

def _clear_all_memory(file_path: str = DEFAULT_MEMORY_FILE) -> str:
    try:
        _write_memory(file_path, {})
        return "Successfully cleared all memory."
    except Exception as e:
        return f"Error clearing memory: {e}"

# LangGraph Tools

class SaveMemoryInput(BaseModel):
    key: str = Field(description="The key under which to save the value.")
    value: Any = Field(description="The value to save.")
    file_path: Optional[str] = Field(DEFAULT_MEMORY_FILE, description="Optional path to the memory file.")

class SaveToMemoryTool(BaseTool):
    name: str = "save_to_memory"
    description: str = "Saves a key-value pair to a persistent memory file. Use this to remember facts, settings, or any piece of information."
    args_schema: Type[BaseModel] = SaveMemoryInput

    def _run(self, key: str, value: Any, file_path: Optional[str] = DEFAULT_MEMORY_FILE) -> str:
        return _save_to_memory(key, value, file_path if file_path else DEFAULT_MEMORY_FILE)

class RetrieveMemoryInput(BaseModel):
    key: str = Field(description="The key of the value to retrieve.")
    file_path: Optional[str] = Field(DEFAULT_MEMORY_FILE, description="Optional path to the memory file.")

class RetrieveFromMemoryTool(BaseTool):
    name: str = "retrieve_from_memory"
    description: str = "Retrieves a value from memory using its key. Use this to recall previously stored information."
    args_schema: Type[BaseModel] = RetrieveMemoryInput

    def _run(self, key: str, file_path: Optional[str] = DEFAULT_MEMORY_FILE) -> any:
        return _retrieve_from_memory(key, file_path if file_path else DEFAULT_MEMORY_FILE)

class DeleteMemoryInput(BaseModel):
    key: str = Field(description="The key of the value to delete.")
    file_path: Optional[str] = Field(DEFAULT_MEMORY_FILE, description="Optional path to the memory file.")

class DeleteFromMemoryTool(BaseTool):
    name: str = "delete_from_memory"
    description: str = "Deletes a key-value pair from memory. Use this to forget a specific piece of information."
    args_schema: Type[BaseModel] = DeleteMemoryInput

    def _run(self, key: str, file_path: Optional[str] = DEFAULT_MEMORY_FILE) -> str:
        return _delete_from_memory(key, file_path if file_path else DEFAULT_MEMORY_FILE)

class GetAllMemoryInput(BaseModel):
    file_path: Optional[str] = Field(DEFAULT_MEMORY_FILE, description="Optional path to the memory file.")

class GetAllMemoryTool(BaseTool):
    name: str = "get_all_memory"
    description: str = "Retrieves all key-value pairs currently stored in memory. Use this to get a dump of everything the agent remembers."
    args_schema: Type[BaseModel] = GetAllMemoryInput

    def _run(self, file_path: Optional[str] = DEFAULT_MEMORY_FILE) -> dict:
        return _get_all_memory(file_path if file_path else DEFAULT_MEMORY_FILE)

class ClearAllMemoryInput(BaseModel):
    file_path: Optional[str] = Field(DEFAULT_MEMORY_FILE, description="Optional path to the memory file.")

class ClearAllMemoryTool(BaseTool):
    name: str = "clear_all_memory"
    description: str = "Clears all data from the memory file. Use this to make the agent forget everything it has learned through this memory."
    args_schema: Type[BaseModel] = ClearAllMemoryInput

    def _run(self, file_path: Optional[str] = DEFAULT_MEMORY_FILE) -> str:
        return _clear_all_memory(file_path if file_path else DEFAULT_MEMORY_FILE)
