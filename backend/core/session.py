"""
OpenWorker Session State Manager
Manages active operational state, session lifecycles, and registry lookups.
"""

import uuid
import asyncio
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Optional
from pydantic import BaseModel, Field

from backend.config import settings
from backend.core.workspace import Workspace
from backend.core.logger import AuditLogger, LogLevel


class SessionStatus(str, Enum):
    INITIALIZED = "INITIALIZED"
    ANALYZING = "ANALYZING"
    PLANNING = "PLANNING"
    EXECUTING = "EXECUTING"
    VALIDATING = "VALIDATING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class SessionMeta(BaseModel):
    session_id: str
    created_at: str
    status: SessionStatus = SessionStatus.INITIALIZED
    current_task: Optional[str] = None


class Session:
    def __init__(self, session_id: Optional[str] = None):
        self.session_id = session_id or str(uuid.uuid4())
        self.created_at = datetime.now(timezone.utc).isoformat()
        self.status = SessionStatus.INITIALIZED
        self.current_task: Optional[str] = None

        self.workspace = Workspace(self.session_id)
        self.logger = AuditLogger(self.session_id, settings.LOGS_DIR)
        self._lock = asyncio.Lock()

    async def update_status(self, status: SessionStatus, task: Optional[str] = None) -> None:
        async with self._lock:
            self.status = status
            if task:
                self.current_task = task
            await self.logger.log(
                LogLevel.INFO,
                "SessionManager",
                f"State transitioned to {status.value}",
                {"task": self.current_task},
            )

    def to_meta(self) -> SessionMeta:
        return SessionMeta(
            session_id=self.session_id,
            created_at=self.created_at,
            status=self.status,
            current_task=self.current_task,
        )


class SessionRegistry:
    """In-memory active session lookup index."""

    def __init__(self):
        self._sessions: Dict[str, Session] = {}

    def create_session(self) -> Session:
        session = Session()
        self._sessions[session.session_id] = session
        return session

    def get_session(self, session_id: str) -> Optional[Session]:
        return self._sessions.get(session_id)

    async def remove_session(self, session_id: str) -> None:
        session = self._sessions.pop(session_id, None)
        if session:
            await session.workspace.cleanup()


session_registry = SessionRegistry()
