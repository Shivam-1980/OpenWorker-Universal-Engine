"""
OpenWorker Autonomous Agent Engine
"""

import json
from typing import List, Dict, Any
from backend.core.session import Session, LogLevel
from backend.tools.registry import ToolRegistry
from backend.llm.ollama_client import OllamaClient
from backend.llm.prompts import SYSTEM_PROMPT

class OpenWorkerAgent:
    def __init__(self, session: Session, registry: ToolRegistry, client: OllamaClient):
        self.session = session
        self.registry = registry
        self.client = client
        self.messages: List[Dict[str, Any]] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

    async def run(self, user_objective: str, repo_profile_json: str):
        prompt_content = (
            f"OBJECTIVE: {user_objective}\n\n"
            f"REPOSITORY INTELLIGENCE:\n{repo_profile_json}\n\n"
            "Begin by inspecting files using ReadFile if needed, apply required fixes using ReplaceBlock or WriteFile, "
            "and ALWAYS conclude by creating 'README_CHANGES.md' and 'requirements.txt'."
        )
        self.messages.append({"role": "user", "content": prompt_content})

        max_turns = 10
        for turn in range(max_turns):
            await self.session.logger.log(
                LogLevel.THOUGHT, "Agent", f"Querying Qwen3 8B (Turn {turn + 1}/{max_turns})..."
            )

            # Query Ollama
            response_msg = await self.client.chat(
                self.messages, 
                tools=self.registry.get_tool_schemas()
            )
            
            # Save assistant response
            self.messages.append(response_msg)

            # Check for tool execution requests
            tool_calls = response_msg.get("tool_calls", [])
            if not tool_calls:
                await self.session.logger.log(LogLevel.INFO, "Agent", "Agent completed task without further tool calls.")
                break

            for tool_call in tool_calls:
                fn_name = tool_call["function"]["name"]
                fn_args = tool_call["function"]["arguments"]
                if isinstance(fn_args, str):
                    fn_args = json.loads(fn_args)

                await self.session.logger.log(
                    LogLevel.TOOL_CALL, "Agent", f"Tool requested: {fn_name}", fn_args
                )

                success, result = await self.registry.execute_tool(
                    fn_name, self.session.workspace, fn_args
                )

                await self.session.logger.log(
                    LogLevel.TOOL_RESULT, "Agent", f"Tool output: {fn_name}", {"success": success,"output":result[:150]}
                )

                # Feed execution result back into chat history
                self.messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.get("id", "call_1"),
                    "name": fn_name,
                    "content": result
                })
