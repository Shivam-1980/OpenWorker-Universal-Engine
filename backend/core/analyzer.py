import asyncio
import sys
from pathlib import Path

class CodeAnalyzer:
    def __init__(self, workspace_source_path: Path):
        self.workspace = workspace_source_path

    async def run_diagnostics(self, filename: str) -> tuple:
        """
        Runs static analysis on the file to enforce standards before compilation.
        Returns (is_valid: bool, logs: str)
        """
        ext = filename.split('.')[-1]
        
        # Define strict linters for systems and web code
        linters = {
            "cpp": f"clang-tidy {filename} -checks='cppcoreguidelines-*,modernize-*,performance-*' --warnings-as-errors=*",
            "c": f"clang-tidy {filename} -checks='clang-analyzer-*,cert-*' --warnings-as-errors=*",
            "js": f"eslint {filename}",
            "html": f"htmlhint {filename}"
        }

        if ext not in linters:
            return True, "[!] No static analyzer configured for this extension. Proceeding to compiler."

        cmd = linters[ext]

        try:
            process = await asyncio.create_subprocess_shell(
                cmd,
                cwd=self.workspace,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()
            logs = stdout.decode(errors='replace') + stderr.decode(errors='replace')
            
            # If returncode is not 0, the linter caught non-standard or unsafe code
            if process.returncode != 0:
                return False, logs
                
            return True, "Code passed all static analysis checks."
            
        except Exception as e:
            return False, f"Static Analysis Engine Failure: {str(e)}"
