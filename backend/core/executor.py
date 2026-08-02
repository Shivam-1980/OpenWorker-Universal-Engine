import asyncio
import sys
from pathlib import Path

class CodeExecutor:
    def __init__(self, workspace_source_path: Path):
        self.workspace = workspace_source_path

    async def compile_and_run(self, filename: str) -> tuple:
        """
        Compiles and executes the code natively based on file extension.
        Returns (stdout, stderr).
        """
        ext = filename.split('.')[-1]
        exe_name = "app.exe" if sys.platform == "win32" else "./app"

        # Build profiles for standard toolchains
        # Note: Swap 'g++' with 'cl.exe /EHsc /MD' if using MSVC for DirectX workflows
        commands = {
            "cpp": f"g++ -O3 {filename} -o {exe_name} && {exe_name}",
            "c": f"gcc -O3 {filename} -o {exe_name} && {exe_name}",
            "cu": f"nvcc {filename} -o {exe_name} && {exe_name}",
            "py": f"python {filename}"
        }

        if ext not in commands:
            return "", f"System Error: No execution profile mapped for .{ext} files."

        cmd = commands[ext]

        try:
            process = await asyncio.create_subprocess_shell(
                cmd,
                cwd=self.workspace,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()
            return stdout.decode(errors='replace'), stderr.decode(errors='replace')
            
        except Exception as e:
            return "", f"Execution Framework Error: {str(e)}"
