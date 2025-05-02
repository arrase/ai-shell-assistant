import subprocess
import logging
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
    Enabling this tool carries significant security risks. It can lead to data breaches,
    system compromise, data loss, and other severe security incidents.
    Use ONLY in highly controlled, isolated environments (e.g., sandboxed containers)
    and after a thorough security review. Never expose this tool in production
    or on systems with sensitive data without extreme caution and robust security measures.
    Consider alternatives like specific tools for specific tasks or strict command whitelisting.
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
    # return_direct: bool = False # Por defecto es False, la salida vuelve al LLM

    def _run(self, command: str, **kwargs: Any) -> str:
        """Executes the Linux command."""
        logger.info(f"Attempting to execute Linux command: {command}")

        # *** Punto Crítico de Seguridad: shell=True ***
        # shell=True permite interpretar la cadena 'command' directamente por el shell
        # del sistema (/bin/sh por defecto). Esto es conveniente para usar pipes (|),
        # redirecciones (>, <), variables de entorno ($HOME), etc., pero es
        # PELIGROSO si 'command' proviene de una fuente no confiable, ya que
        # permite la inyección de comandos (ej: "ls; rm -rf /").
        #
        # Alternativa más segura (pero menos flexible):
        # Usar shell=False y pasar el comando como una lista. Requiere parsear
        # el comando de forma segura, por ejemplo con shlex.split().
        # Ejemplo: args = shlex.split(command) -> subprocess.run(args, ...)
        # Sin embargo, esto no soporta pipes, redirecciones, etc. directamente.
        # Dado que la petición es ejecutar "cualquier" comando, mantenemos shell=True
        # pero con la máxima advertencia.

        try:
            process = subprocess.run(
                command,
                shell=True,                 # ¡¡ALERTA DE SEGURIDAD!!
                capture_output=True,        # Captura stdout y stderr
                text=True, # Decodifica stdout/stderr como texto (usa encoding por defecto)
                check=False, # No lanza excepción si el comando falla (returncode != 0)
                timeout=60 # Añadir un timeout para evitar bloqueos (ajustar según necesidad)
            )

            # Formatear la salida para el agente
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
        """Asynchronous execution of the Linux command (opcional)."""
        # Para una implementación asíncrona real, se usaría asyncio.create_subprocess_shell
        # Por simplicidad aquí, llamamos a la versión síncrona en un executor.
        # Si necesita concurrencia real, debería implementarse con asyncio.
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._run, command)
