import subprocess
import logging
import asyncio

from typing import Type, Any
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


class LinuxCommandInput(BaseModel):
    """Input schema for the Linux Command Execution tool."""
    command: str = Field(...,
                         description="The Linux shell command to be executed.")


class ExecuteLinuxCommandTool(BaseTool):
    """
    Tool that executes a Linux shell command on the host system where the agent is running.

    *** CRITICAL SECURITY WARNING ***
    This tool allows arbitrary code execution on the host system.
    """
    name: str = "execute_linux_command"
    description: str = (
        "Executes a given Linux shell command and returns its standard output, standard error, and return code."
        "Use this tool to interact with the underlying Linux operating system."
        "Input must be a single string containing the command to execute."
        "Example: 'ls -la /tmp'."
        "WARNING: Executes commands with the privileges of the agent process. HIGH SECURITY RISK."
    )
    args_schema: Type[BaseModel] = LinuxCommandInput

    def _run(self, command: str, **kwargs: Any) -> str:
        """Executes the Linux command."""
        logger.info(f"Attempting to execute Linux command: {command}")

        try:
            process = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                check=False,
                timeout=60
            )

            output = f"Executing command: {command}\n"
            output += f"Return Code: {process.returncode}\n"
            if process.stdout:
                output += f"--- Standard Output ---\n{process.stdout.strip()}\n"
            else:
                output += "--- Standard Output ---\n(No standard output)\n"

            if process.stderr:
                output += f"--- Standard Error ---\n{process.stderr.strip()}\n"
            else:
                output += "--- Standard Error ---\n(No standard error)\n"

            logger.info(f"Command executed. Return Code: {process.returncode}")

            return output.strip()

        except subprocess.TimeoutExpired:
            logger.error(f"Command '{command}' timed out.")
            return f"Error: Command '{command}' timed out after 60 seconds."
        except Exception as e:
            logger.error(
                f"Error executing command '{command}': {e}", exc_info=True)
            return f"Error executing command '{command}': {str(e)}"

    async def _arun(self, command: str, **kwargs: Any) -> str:
        """Asynchronous execution of the Linux command."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._run, command)
