import subprocess
import logging
import asyncio

from typing import Type, Any
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


class ShellCommand(BaseModel):
    """Input schema for the Execute Shell Command Tool."""
    command: str = Field(..., description="The shell command to be executed.")


class ExecuteShellCommandTool(BaseTool):
    """
    Tool that executes a shell command on the host system where the agent is running.

    *** CRITICAL SECURITY WARNING ***
    This tool allows arbitrary code execution on the host system.
    """
    name: str = "execute_shell_command"
    description: str = (
        "This tool executes a shell command on the host system and returns the results, including the command's output, error messages, and return code."
        "Use this tool to interact with the operating system by providing a single string containing the command to execute."
        "Input format: A single string representing the shell command (e.g., 'ls -la /tmp')."
        "Output format: A structured response containing:"
        "1. The executed command."
        "2. The return code of the command."
        "3. A section labeled '--- Standard Output ---' with the command's standard output or '(No standard output)' if empty."
        "4. A section labeled '--- Standard Error ---' with the command's standard error or '(No standard error)' if empty."
        "WARNING: This tool executes commands with the same privileges as the agent process, which poses a HIGH SECURITY RISK. Ensure commands are sanitized and safe before execution."
    )

    args_schema: Type[BaseModel] = ShellCommand

    def _run(self, command: str, **kwargs: Any) -> str:
        """Executes the shell command."""
        logger.info(f"Attempting to execute shell command: {command}")

        try:
            process = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                check=False,
                timeout=60
            )

            output = [
                f"Executing command: {command}",
                f"Return Code: {process.returncode}",
                "--- Standard Output ---",
                process.stdout.strip() if process.stdout else "(No standard output)",
                "--- Standard Error ---",
                process.stderr.strip() if process.stderr else "(No standard error)"
            ]

            logger.info(f"Command executed. Return Code: {process.returncode}")
            return "\n".join(output)

        except subprocess.TimeoutExpired:
            error_message = f"Error: Command '{command}' timed out after 60 seconds."
            logger.error(error_message)
            return error_message
        except Exception as e:
            error_message = f"Error executing command '{command}': {str(e)}"
            logger.error(error_message, exc_info=True)
            return error_message

    async def _arun(self, command: str, **kwargs: Any) -> str:
        """Asynchronous execution of the shell command."""
        return await asyncio.to_thread(self._run, command)
