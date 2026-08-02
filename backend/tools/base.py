"""
OpenWorker Base Tool Interface
Defines the contract for all actionable tools in the system.
"""

from typing import Any, Dict
from backend.core.workspace import Workspace

class BaseTool:
    name: str = "BaseTool"
    description: str = "Base description"
    parameters: Dict[str, Any] = {}

    async def execute(self, workspace: Workspace, **kwargs) -> str:
        """
        Executes the tool's core logic.
        Must return a string representing the outcome (success or error details).
        """
        raise NotImplementedError("Tools must implement the execute method.")
