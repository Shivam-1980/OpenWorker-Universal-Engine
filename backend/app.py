"""
OpenWorker Application Entry Point
Exposes high-performance REST APIs and real-time SSE streaming feeds.
"""

import tempfile
import asyncio
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse

from backend.config import settings
from backend.core.session import session_registry, SessionStatus
from backend.core.logger import LogLevel

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="An Autonomous Software Engineering Worker Platform API",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/v1/health")
async def health_check():
    return {"status": "ok", "version": settings.VERSION}


@app.post("/api/v1/sessions/upload")
async def upload_workspace(file: UploadFile = File(...)):
    """Uploads a ZIP project, initializes a sandboxed workspace, and creates a session."""
    if not file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="Only .zip files are supported.")

    session = session_registry.create_session()

    try:
        # Save uploaded bytes to a temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp:
            tmp_path = Path(tmp.name)
            content = await file.read()
            tmp_path.write_bytes(content)

        # Extract archive safely into workspace
        await session.workspace.extract_archive(tmp_path)
        tmp_path.unlink(missing_ok=True)  # Clean up temp archive file

        await session.logger.log(
            LogLevel.INFO,
            "API",
            "Uploaded workspace extracted successfully.",
            {"filename": file.filename},
        )

        return {
            "session_id": session.session_id,
            "status": session.status,
            "message": "Workspace initialized successfully.",
        }

    except Exception as e:
        await session_registry.remove_session(session.session_id)
        raise HTTPException(status_code=500, detail=f"Failed to initialize workspace: {str(e)}")


@app.get("/api/v1/sessions/{session_id}/stream")
async def stream_audit_logs(session_id: str):
    """Real-time SSE endpoint streaming audit logs to the frontend."""
    session = session_registry.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    async def event_generator():
        async for event in session.logger.subscribe():
            yield f"data: {event.model_dump_json()}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.get("/api/v1/sessions/{session_id}/download")
async def download_workspace(session_id: str):
    """Exports and serves the modified project workspace as a ZIP file."""
    session = session_registry.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    export_path = await session.workspace.compress_workspace()
    return FileResponse(
        path=export_path,
        filename=f"openworker_{session_id}.zip",
        media_type="application/zip",
    )
