"""
Console stream subscriber for OpenWorker audit logs.
"""

import asyncio
from backend.core.logger import LogLevel

async def stream_logs_to_console(session):
    COLORS = {
        LogLevel.INFO: "\033[94m",
        LogLevel.WARNING: "\033[93m",
        LogLevel.ERROR: "\033[91m",
        LogLevel.THOUGHT: "\033[96m",
        LogLevel.TOOL_CALL: "\033[95m",
        LogLevel.TOOL_RESULT: "\033[92m",
    }
    RESET = "\033[0m"

    try:
        async for event in session.logger.subscribe():
            color = COLORS.get(event.level, "")
            print(f"{color}[{event.timestamp}] [{event.level}] {event.source}: {event.message}{RESET}")
            if event.payload:
                print(f"      Payload: {event.payload}")
    except asyncio.CancelledError:
        return
