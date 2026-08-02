"""
OpenWorker Ollama Async Client
"""

import httpx
from typing import List, Dict, Any, Optional

class OllamaClient:
    def __init__(self, model: str = "qwen3:8b", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url.rstrip("/")

    async def chat(self, messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        # Set timeout to None so long context window generations are not killed
        timeout_config = httpx.Timeout(None, connect=10.0)
        
        formatted_tools = None
        if tools:
            formatted_tools = []
            for t in tools:
                if isinstance(t, dict) and t.get("type") == "function":
                    formatted_tools.append(t)
                else:
                    formatted_tools.append({
                        "type": "function",
                        "function": t
                    })

        async with httpx.AsyncClient(timeout=timeout_config) as client:
            payload = {
                "model": self.model,
                "messages": messages,
                "stream": False,
                "keep_alive": "10m"
            }
            if formatted_tools:
                payload["tools"] = formatted_tools

            try:
                response = await client.post(f"{self.base_url}/api/chat", json=payload)
                response.raise_for_status()
                data = response.json()
                
                return data.get("message", {})

            except httpx.HTTPStatusError as e:
                raise RuntimeError(f"Ollama Returned HTTP {e.response.status_code}: {e.response.text}") from e
            except httpx.RequestError as e:
                raise RuntimeError(f"Could not connect to Ollama at {self.base_url}.") from e
