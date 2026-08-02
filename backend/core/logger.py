"""
OpenWorker Structured Audit Logger
Records every agent action, tool invocation, and decision for full replayability.
"""

import json
import asyncio
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional
from pydantic import BaseModel


class LogLevel(str, Enum):
    INFO = "INFO"
    THOUGHT = "THOUGHT"
    TOOL_CALL = "TOOL_CALL"
    TOOL_RESULT = "TOOL_RESULT"
    WARNING = "WARNING"
    ERROR = "ERROR"


class LogEvent(BaseModel):
    timestamp: str
    session_id: str
    level: LogLevel
    source: str
    message: str
    payload: Optional[Dict[str, Any]] = None


class AuditLogger:
    def __init__(self, session_id: str, log_dir: Path):
        self.session_id = session_id
        self.log_file = log_dir / f"{session_id}.jsonl"
        self._event_queue: asyncio.Queue[LogEvent] = asyncio.Queue()

    async def log(
        self,
        level: LogLevel,
        source: str,
        message: str,
        payload: Optional[Dict[str, Any]] = None,
    ) -> LogEvent:
        event = LogEvent(
            timestamp=datetime.now(timezone.utc).isoformat(),
            session_id=self.session_id,
            level=level,
            source=source,
            message=message,
            payload=payload or {},
        )

        # Python 3.8 compatible async thread dispatch
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self._write_to_disk, event)

        # Dispatch to real-time subscribers
        await self._event_queue.put(event)
        return event

    def _write_to_disk(self, event: LogEvent) -> None:
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(event.model_dump_json() + "\n")

    async def subscribe(self):
        """Async generator yields events in real-time for SSE streaming."""
        while True:
            event = await self._event_queue.get()
            yield event
            self._event_queue.task_done()
