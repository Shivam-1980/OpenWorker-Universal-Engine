"""
OpenWorker Tool Registry with Argument Normalization
"""

from typing import Dict, Any, Tuple
from backend.core.workspace import Workspace
from backend.tools.base import BaseTool
from backend.tools.filesystem import ReadFileTool, WriteFileTool, ReplaceBlockTool
from backend.tools.terminal import BuildAndTestTool

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
        self._register_defaults()

    def _register_defaults(self):
        for tool_class in [ReadFileTool, WriteFileTool, ReplaceBlockTool, BuildAndTestTool]:
            tool_instance = tool_class()
            self._tools[tool_instance.name] = tool_instance

    def get_tool_schemas(self) -> list:
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters
            }
            for tool in self._tools.values()
        ]

    async def execute_tool(self, tool_name: str, workspace: Workspace, kwargs: Dict[str, Any]) -> Tuple[bool, str]:
        tool = self._tools.get(tool_name)
        if not tool:
            return False, f"Error: Tool '{tool_name}' is not registered."

        # Alias mapping to catch common LLM parameter substitutions
        ALIAS_MAP = {
            "filename": "filepath",
            "file_path": "filepath",
            "path": "filepath",
            "file": "filepath",
            "code": "content",
            "text": "content",
            "start": "start_line",
            "end": "end_line",
            "cmd": "command"
        }

        # Normalize arguments
        normalized_kwargs = {}
        for key, val in kwargs.items():
            norm_key = ALIAS_MAP.get(key.lower(), key)
            normalized_kwargs[norm_key] = val

        try:
            result = await tool.execute(workspace, **normalized_kwargs)
            is_success = not result.startswith("Error") and not result.startswith("Security Error")
            return is_success, result

        except TypeError as e:
            return False, f"Tool argument mismatch: {str(e)}. Accepted parameters: {list(tool.parameters.keys())}"
        except Exception as e:
            return False, f"Fatal tool execution error: {str(e)}"
