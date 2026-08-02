# web/sandbox.py
import docker
import asyncio
import shutil
import subprocess
from pathlib import Path

class CompilerSandbox:
    def __init__(self, workspace_path: Path):
        self.workspace_path = workspace_path

    def detect_available_toolchains(_self) -> dict:
        """Probes the system for active compilers."""
        tools = ['cl.exe', 'g++', 'nvcc', 'cmake', 'npm', 'iverilog', 'python']
        return {tool: shutil.which(tool) is not None for tool in tools}

    def execute_build(self, command: str) -> tuple[int, str]:
        """Runs the build/compile command directly inside the project directory."""
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=str(self.workspace_path),
                capture_output=True,
                text=True,
                timeout=120
            )
            output = result.stdout + ("\n--- STDERR ---\n" + result.stderr if result.stderr else "")
            return result.returncode, output
        except subprocess.TimeoutExpired:
            return -1, "Execution timed out after 120 seconds."
        except Exception as e:
            return -1, f"Sandbox Failure: {str(e)}"



class DockerSandbox:
    def __init__(self, workspace_path: Path, session_id: str):
        self.workspace_path = str(workspace_path.absolute())
        self.container_name = f"openworker_env_{session_id}"
        self.container = None
        
        try:
            self.client = docker.from_env()
        except Exception as e:
            raise RuntimeError(
                "Docker daemon is not running. Please launch Docker Desktop "
                "to enable the autonomous container execution environment."
            ) from e

    def start(self):
        try:
            self.container = self.client.containers.run(
                "gcc:latest", 
                name=self.container_name,
                command="tail -f /dev/null",
                detach=True,
                volumes={self.workspace_path: {'bind': '/workspace', 'mode': 'rw'}},
                working_dir="/workspace",
                auto_remove=True
            )
            return True, "Sandbox initialized."
        except Exception as e:
            return False, f"Failed to initialize sandbox: {str(e)}"

    async def execute_bash_streaming(self, command: str, websocket) -> int:
        if not self.container:
            await websocket.send_text('{"stderr": "Sandbox is not running."}')
            return 1
            
        try:
            exec_id = self.client.api.exec_create(
                self.container.id, 
                cmd=['/bin/bash', '-c', command],
                workdir="/workspace"
            )
            
            stream = self.client.api.exec_start(exec_id['Id'], stream=True)
            
            for chunk in stream:
                decoded = chunk.decode('utf-8', errors='replace')
                await websocket.send_text(json.dumps({
                    "stdout": decoded
                }))
            
            inspect = self.client.api.exec_inspect(exec_id['Id'])
            return inspect['ExitCode']
            
        except Exception as e:
            await websocket.send_text(json.dumps({"stderr": f"Sandbox Exception: {str(e)}"}))
            return 1

    def terminate(self):
        if self.container:
            try:
                self.container.stop()
            except:
                pass
