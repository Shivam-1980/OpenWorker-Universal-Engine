import asyncio
import os
from pathlib import Path
import json
import shutil
import platform
import time
import re

class DockerSandbox:
    """Dynamic local execution sandbox executing commands emitted by the AI agent."""
    def __init__(self, workspace_path: Path, session_id: str):
        self.session_id = session_id
        self.workspace_path = Path(workspace_path).resolve()
        self.workspace_path.mkdir(parents=True, exist_ok=True)
        self.os_type = platform.system()

    def start(self):
        return True, f"Sandbox initialized for OS: {self.os_type}"

    async def run_ai_directive(self, ai_response_text: str, websocket, timeout: int = 120) -> int:
        """Parses and executes shell commands emitted directly by the AI agent inside <command> tags."""
        
        # 1. Handle Web Preview Directive
        if "<preview/>" in ai_response_text:
            await websocket.send_text(json.dumps({
                "stdout": "\n[System] Live Web Preview requested by Agent.\n",
                "status_update": "IDLE"
            }))
            return 0

        # 2. Extract and run command directives
        match = re.search(r"<command>(.*?)</command>", ai_response_text, re.DOTALL)
        if not match:
            return 0  # No build step requested by AI

        command = match.group(1).strip()
        
        # Windows command path translation
        if self.os_type == "Windows":
            command = command.replace("./", ".\\")

        await websocket.send_text(json.dumps({
            "stdout": f"\n$ {command}\n",
            "status_update": "EXECUTING"
        }))
        
        start_time = time.time()
        exit_code = await self._run_subprocess(command, websocket, timeout)
        elapsed = round(time.time() - start_time, 3)
        
        await websocket.send_text(json.dumps({
            "stdout": f"\n[Process completed with exit code {exit_code} in {elapsed}s]\n",
            "status_update": "IDLE"
        }))
        return exit_code

    async def _run_subprocess(self, command: str, websocket, timeout: int) -> int:
        try:
            process = await asyncio.create_subprocess_shell(
                command,
                cwd=self.workspace_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            async def read_stream(stream, is_error=False):
                while True:
                    line = await stream.readline()
                    if not line:
                        break
                    decoded = line.decode('utf-8', errors='replace')
                    await websocket.send_text(json.dumps({
                        "stderr" if is_error else "stdout": decoded
                    }))

            try:
                await asyncio.wait_for(
                    asyncio.gather(
                        read_stream(process.stdout, is_error=False),
                        read_stream(process.stderr, is_error=True)
                    ),
                    timeout=timeout
                )
                await process.wait()
                return process.returncode

            except asyncio.TimeoutError:
                try:
                    process.kill()
                except Exception:
                    pass
                await websocket.send_text(json.dumps({
                    "stderr": f"\n[!] Process timed out after {timeout}s and was terminated.\n"
                }))
                return 1

        except Exception as e:
            await websocket.send_text(json.dumps({"stderr": f"Sandbox Exception: {str(e)}"}))
            return 1

    def terminate(self):
        try:
            if self.workspace_path.exists():
                shutil.rmtree(self.workspace_path)
        except Exception:
            pass
