import asyncio
import os
from pathlib import Path
import json
import shutil

class MicroSandbox:
    def __init__(self, session_id: str, base_dir: str = "./sandboxes"):
        self.session_id = session_id
        # Give every user session its own completely isolated directory
        self.sandbox_path = Path(base_dir).resolve() / session_id
        self.sandbox_path.mkdir(parents=True, exist_ok=True)

    def get_path(self) -> Path:
        return self.sandbox_path

    async def execute_streaming(self, command: str, websocket, timeout: int = 20) -> int:
        """
        Executes a shell command inside the isolated session directory.
        Includes a strict timeout guard to prevent infinite loops or lockups.
        """
        try:
            process = await asyncio.create_subprocess_shell(
                command,
                cwd=self.sandbox_path,
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
                # Enforce execution timeout (default 20 seconds)
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
                # Kill the process if it runs too long (e.g., infinite compilation or loop)
                try:
                    process.kill()
                except Exception:
                    pass
                
                await websocket.send_text(json.dumps({
                    "stderr": f"\n[!] Sandbox Alert: Process timed out after {timeout}s and was killed.\n"
                }))
                return 1

        except Exception as e:
            await websocket.send_text(json.dumps({"stderr": f"MicroSandbox Exception: {str(e)}"}))
            return 1

    def destroy(self):
        """Wipes the session sandbox clean when the user leaves."""
        try:
            if self.sandbox_path.exists():
                shutil.rmtree(self.sandbox_path)
        except Exception:
            pass
