"""
OpenWorker Architect Phase
Forces the LLM to research and output a definitive execution plan before coding.
"""

import json
from typing import List, Dict, Any
from backend.core.session import Session, LogLevel
from backend.tools.registry import ToolRegistry
from backend.llm.ollama_client import OllamaClient

ARCHITECT_PROMPT = """You are the Lead Systems Architect and Principal Engineer.
Your goal is to analyze the user's objective and the repository context (which may be empty if building from scratch).
1. If the repository is empty or missing necessary files, you must design the entire file structure and system architecture from first principles.
2. Use the WebSearch tool to research documentation, APIs, or best practices if needed.
3. Formulate a rigorous, step-by-step execution plan covering math, data structures, and memory management.
4. Always conclude your planning phase by creating a comprehensive 'PLAN.md' using the WriteFile tool.
Do NOT start writing the final source code implementation yet. Your ONLY output during this phase is the architectural plan."""

class ArchitectAgent:
    def __init__(self, session: Session, registry: ToolRegistry, client: OllamaClient):
        self.session = session
        self.registry = registry
        self.client = client
        self.messages: List[Dict[str, Any]] = [
            {"role": "system", "content": ARCHITECT_PROMPT}
        ]

    async def draft_plan(self, user_objective: str, repo_profile_json: str) -> bool:
        prompt_content = (
            f"OBJECTIVE: {user_objective}\n\n"
            f"REPOSITORY CONTEXT:\n{repo_profile_json}\n\n"
            "Analyze the system, use WebSearch if you lack specific API knowledge, "
            "and write 'PLAN.md' using the WriteFile tool. Then stop."
        )
        self.messages.append({"role": "user", "content": prompt_content})

        max_turns = 5
        for turn in range(max_turns):
            await self.session.logger.log(
                LogLevel.THOUGHT, "Architect", f"Drafting Architecture (Turn {turn + 1}/{max_turns})..."
            )

            response_msg = await self.client.chat(
                self.messages, 
                tools=self.registry.get_tool_schemas()
            )
            self.messages.append(response_msg)

            tool_calls = response_msg.get("tool_calls", [])
            if not tool_calls:
                await self.session.logger.log(LogLevel.INFO, "Architect", "Planning phase complete.")
                return True

            for tool_call in tool_calls:
                fn_name = tool_call["function"]["name"]
                fn_args = tool_call["function"]["arguments"]
                if isinstance(fn_args, str):
                    fn_args = json.loads(fn_args)

                await self.session.logger.log(LogLevel.TOOL_CALL, "Architect", f"Executing: {fn_name}", fn_args)

                success, result = await self.registry.execute_tool(fn_name, self.session.workspace, fn_args)

                self.messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.get("id", f"call_{turn}"),
                    "name": fn_name,
                    "content": result
                })

                # If the Architect successfully wrote the plan, exit early
                if fn_name == "WriteFile" and "PLAN.md" in str(fn_args):
                    await self.session.logger.log(LogLevel.INFO, "Architect", "PLAN.md successfully generated.")
                    return True

        return False
