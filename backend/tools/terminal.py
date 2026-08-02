"""
OpenWorker Terminal & Build Execution Tool
Executes sandboxed build commands (cmake, g++, pytest, python) and captures stdout/stderr.
"""

import asyncio
import subprocess
from pathlib import Path
from backend.tools.base import BaseTool
from backend.core.workspace import Workspace, SecurityError

class BuildAndTestTool(BaseTool):
    name = "BuildAndTest"
    description = (
        "Executes a safe build or test command (e.g., 'cmake -B build', 'g++ src/main.cpp', 'pytest') "
        "inside the workspace root and returns stdout/stderr to verify if code compiles without errors."
    )
    parameters = {
        "command": "The build/test shell command to execute (e.g., 'g++ -c src/Renderer.cpp -I src')."
    }

    # Safe command whitelist to prevent system compromise
    ALLOWED_COMMANDS = {"g++", "gcc", "cmake", "make", "ctest", "pytest", "python", "python3", "ninja","nmake","npm","node","msbuild"}

    async def execute(self, workspace: Workspace, command: str, **kwargs) -> str:
        tokens = command.strip().split()
        if not tokens:
            return "Error: Empty command provided."

        executable = tokens[0].lower()
        if executable not in self.ALLOWED_COMMANDS:
            return f"Security Error: Execution of '{executable}' is forbidden. Allowed: {list(self.ALLOWED_COMMANDS)}"

        try:
            # Execute inside workspace source directory
            cwd = workspace.source_path

            def _run():
                process = subprocess.run(
                    command,
                    shell=True,
                    cwd=cwd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=30 # 30s timeout to prevent infinite build loops
                )
                return process.returncode, process.stdout, process.stderr

            loop = asyncio.get_running_loop()
            returncode, stdout, stderr = await loop.run_in_executor(None, _run)

            output = f"Exit Code: {returncode}\n"
            if stdout:
                output += f"--- STDOUT ---\n{stdout[:2000]}\n" # Truncate long build logs
            if stderr:
                output += f"--- STDERR ---\n{stderr[:2000]}\n"

            return output

        except subprocess.TimeoutExpired:
            return "Error: Build/Test process timed out after 30 seconds."
        except Exception as e:
            return f"Error executing command: {str(e)}"
