import os
import tempfile
import logging
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from web.sockets import router as socket_router
from backend.core.workspace import Workspace

# Configure structured logging for live debugging[cite: 3]
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("OpenWorkerServer")

# 1. Initialize FastAPI app instance FIRST[cite: 3]
app = FastAPI(title="AI Engineer Backend")

# 2. Ensure static directory exists[cite: 3]
os.makedirs("web/static", exist_ok=True)
logger.info("Static directory 'web/static' verified/created.")

# 3. Include WebSocket routes[cite: 3]
app.include_router(socket_router)
logger.info("WebSocket router successfully included.")

# 4. API Endpoints for File Upload / Project ZIP Ingestion[cite: 3]
@app.post("/api/upload/{session_id}")
async def handle_file_upload(session_id: str, file: UploadFile = File(...)):
    logger.info(f"[UPLOAD] Session ID: {session_id} | Ingesting file: {file.filename}")
    workspace = Workspace(session_id)
    
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_path = Path(temp_file.name)
        content = await file.read()
        temp_path.write_bytes(content)

    try:
        if file.filename.endswith(".zip"):
            logger.info(f"[UPLOAD] Unpacking ZIP archive: {file.filename} for session {session_id}")
            await workspace.extract_archive(temp_path)
            message = f"Unpacked ZIP archive: {file.filename}"
        else:
            logger.info(f"[UPLOAD] Writing single file: {file.filename} for session {session_id}")
            await workspace.write_file(file.filename, content.decode("utf-8", errors="ignore"))
            message = f"Ingested single file: {file.filename}"
    finally:
        if temp_path.exists():
            temp_path.unlink()

    tree_map = await workspace.get_tree_map()
    logger.info(f"[UPLOAD] Success for session {session_id}. Current workspace tree nodes: {len(tree_map)}")
    return {
        "status": "success",
        "message": message,
        "tree": tree_map
    }

# 5. API Endpoint for Downloading Exported Project ZIP[cite: 3]
@app.get("/api/download/{session_id}")
async def handle_file_download(session_id: str):
    logger.info(f"[DOWNLOAD] Export bundle requested for session: {session_id}")
    workspace = Workspace(session_id)
    zip_path = await workspace.compress_workspace()
    
    if not zip_path.exists():
        logger.error(f"[DOWNLOAD] Failed to generate zip bundle at {zip_path} for session {session_id}")
        raise HTTPException(status_code=404, detail="Export bundle could not be generated.")
        
    logger.info(f"[DOWNLOAD] Serving export archive: {zip_path}")
    return FileResponse(
        path=zip_path, 
        filename=f"openworker_{session_id}.zip", 
        media_type="application/zip"
    )

# 6. API Endpoint for Fetching Workspace Files with Robust Windows Path Error Prevention
@app.get("/api/workspace/{session_id}/files")
async def get_workspace_files(session_id: str):
    logger.debug(f"[FILES] Polling file tree for session: {session_id}")
    try:
        # Use an absolute path resolved safely to prevent Windows device namespace errors
        base_dir = Path("workspaces").resolve()
        workspace_path = (base_dir / session_id).resolve()
        
        # Ensure it stays safely within the workspaces directory boundary
        if not str(workspace_path).startswith(str(base_dir)):
            logger.warning(f"[FILES SECURITY] Invalid path traversal attempted: {session_id}")
            raise HTTPException(status_code=400, detail="Invalid session path")
            
        workspace_path.mkdir(parents=True, exist_ok=True)
        
        files = [
            str(p.relative_to(workspace_path)).replace("\\", "/") 
            for p in workspace_path.rglob("*") if p.is_file()
        ]
        logger.debug(f"[FILES] Returning {len(files)} files for session {session_id}")
        return {"files": files}
    except Exception as e:
        logger.error(f"[FILES ERROR] Failed to retrieve files for session {session_id}: {e}", exc_info=True)
        return {"files": []}

# 7. API Endpoint for Reading Individual Workspace Files[cite: 3]
@app.get("/api/workspace/{session_id}/read")
async def read_workspace_file(session_id: str, file: str):
    logger.info(f"[READ] Session: {session_id} | Requested file read: {file}")
    base_dir = Path("workspaces").resolve()
    workspace_path = (base_dir / session_id).resolve()
    file_path = (workspace_path / file).resolve()
    
    # Security check against path traversal[cite: 3]
    if not str(file_path).startswith(str(workspace_path)) or not file_path.is_file():
        logger.warning(f"[READ SECURITY] Path traversal violation or missing file attempted: '{file}' in session {session_id}")
        raise HTTPException(status_code=404, detail="File not found")
        
    logger.info(f"[READ] Successfully serving file path: {file_path}")
    return FileResponse(path=file_path)

# 8. Mount Static Frontend LAST so it doesn't mask API/WebSocket routes[cite: 3]
app.mount("/", StaticFiles(directory="web/static", html=True), name="static")
logger.info("Static frontend mounted successfully at root '/' path.")
