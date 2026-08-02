"""
OpenWorker Web Search Tool
Allows the agent to query the internet for documentation, API references, and error fixes.
"""

import asyncio
from duckduckgo_search import DDGS
from backend.tools.base import BaseTool
from backend.core.workspace import Workspace

class WebSearchTool(BaseTool):
    name = "WebSearch"
    description = (
        "Searches the web for technical documentation, code examples, or bug fixes. "
        "Use this when you need up-to-date information on an API or framework."
    )
    parameters = {
        "query": "The specific search query (e.g., 'DirectX 12 CreateCommandQueue example C++').",
        "max_results": "Number of results to return (integer, max 5, default 3)."
    }

    async def execute(self, workspace: Workspace, query: str, max_results: int = 3, **kwargs) -> str:
        if not query:
            return "Error: Search query cannot be empty."

        try:
            # Run the synchronous DDGS search in a thread pool to avoid blocking the async event loop
            loop = asyncio.get_running_loop()
            
            def _search():
                results = []
                with DDGS() as ddgs:
                    for r in ddgs.text(query, max_results=int(max_results)):
                        results.append(f"Title: {r.get('title')}\nURL: {r.get('href')}\nSnippet: {r.get('body')}\n")
                return results

            search_results = await loop.run_in_executor(None, _search)
            
            if not search_results:
                return f"No results found for query: '{query}'"
                
            return "\n---\n".join(search_results)

        except Exception as e:
            return f"Search Error: {str(e)}"
