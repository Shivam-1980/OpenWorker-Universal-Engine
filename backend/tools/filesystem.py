"""
OpenWorker Filesystem Tools
Provides sandboxed read, write, and targeted patching capabilities.
"""

import asyncio
from backend.tools.base import BaseTool
from backend.core.workspace import Workspace, SecurityError

class ReadFileTool(BaseTool):
    name = "ReadFile"
    description = "Reads a file and returns its content with line numbers for precise editing."
    parameters = {
        "filepath": "Relative path to the file inside the workspace."
    }

    async def execute(self, workspace: Workspace, filepath: str, **kwargs) -> str:
        try:
            target_path = workspace.resolve_path(filepath)
            
            def _read():
                with open(target_path, 'r', encoding='utf-8') as f:
                    # Enumerate adds line numbers (1-indexed) so the AI knows exactly where to edit
                    return "\n".join(f"{i+1:4d} | {line}" for i, line in enumerate(f.read().splitlines()))
                    
            loop = asyncio.get_running_loop()
            content = await loop.run_in_executor(None, _read)
            return f"--- {filepath} ---\n{content}"
            
        except FileNotFoundError:
            return f"Error: File {filepath} not found."
        except SecurityError as e:
            return f"Security Error: {str(e)}"
        except Exception as e:
            return f"Error reading file: {str(e)}"


class WriteFileTool(BaseTool):
    name = "WriteFile"
    description = "Creates a new file or completely overwrites an existing one."
    parameters = {
        "filepath": "Relative path to the file.",
        "content": "The complete new content of the file."
    }

    async def execute(self, workspace: Workspace, filepath: str, content: str, **kwargs) -> str:
        try:
            target_path = workspace.resolve_path(filepath)
            
            def _write():
                target_path.parent.mkdir(parents=True, exist_ok=True)
                with open(target_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, _write)
            return f"Successfully wrote {len(content.splitlines())} lines to {filepath}."
            
        except SecurityError as e:
            return f"Security Error: {str(e)}"
        except Exception as e:
            return f"Error writing file: {str(e)}"


class ReplaceBlockTool(BaseTool):
    name = "ReplaceBlock"
    description = "Replaces a specific block of lines in a file to avoid rewriting the entire file."
    parameters = {
        "filepath": "Relative path to the file.",
        "start_line": "The line number to start replacing (inclusive).",
        "end_line": "The line number to stop replacing (inclusive).",
        "new_content": "The new code block to insert."
    }

    async def execute(self, workspace: Workspace, filepath: str, start_line: int, end_line: int, new_content: str, **kwargs) -> str:
        try:
            target_path = workspace.resolve_path(filepath)
            
            def _replace():
                with open(target_path, 'r', encoding='utf-8') as f:
                    lines = f.read().splitlines()
                
                # Convert 1-indexed to 0-indexed
                start_idx = max(0, start_line - 1)
                end_idx = min(len(lines), end_line)
                
                new_lines = new_content.splitlines()
                # Splice the new content into the original file
                modified_lines = lines[:start_idx] + new_lines + lines[end_idx:]
                
                with open(target_path, 'w', encoding='utf-8') as f:
                    f.write("\n".join(modified_lines) + "\n")
                    
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, _replace)
            return f"Successfully replaced lines {start_line} to {end_line} in {filepath}."
            
        except FileNotFoundError:
            return f"Error: File {filepath} not found."
        except SecurityError as e:
            return f"Security Error: {str(e)}"
        except Exception as e:
            return f"Error replacing block: {str(e)}"
