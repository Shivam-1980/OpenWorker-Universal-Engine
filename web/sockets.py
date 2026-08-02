import json
import re
from pathlib import Path
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from web.core import AIEngine
from backend.core.workspace import Workspace
from backend.core.executor import CodeExecutor
from backend.core.analyzer import CodeAnalyzer
from backend.core.sandbox import DockerSandbox
from backend.core.watcher import DirectoryWatcher
from backend.core.context_loader import ContextLoader
from backend.core.environment import EnvironmentScanner

router = APIRouter()

def parse_llm_response(raw_text: str) -> tuple:
    """Extracts explicit filename tags, code content, and thoughts."""
    file_match = re.search(r'FILE:\s*([\w\.\-]+)', raw_text)
    filename = file_match.group(1) if file_match else None

    code_match = re.search(r'```(?:html|javascript|cpp|c|python|cuda)?\n(.*?)```', raw_text, re.DOTALL)
    
    if code_match:
        code_content = code_match.group(1).strip()
        terminal_log = re.sub(r'```.*?```', '', raw_text, flags=re.DOTALL).strip()
        
        if not filename:
            if "<html>" in code_content.lower() or "<script>" in code_content.lower():
                filename = "index.html"
            elif "#include" in code_content:
                filename = "main.cpp"
            elif "def " in code_content or "import " in code_content:
                filename = "main.py"
            else:
                filename = "main.txt"
                
        return filename, code_content, terminal_log
        
    return "notes.txt", raw_text, raw_text

def parse_diagnostic_response(raw_text: str) -> tuple:
    """Extracts the AI's internal reasoning so the user can read it."""
    diagnosis_match = re.search(r'<diagnosis>(.*?)</diagnosis>', raw_text, re.DOTALL)
    plan_match = re.search(r'<plan>(.*?)</plan>', raw_text, re.DOTALL)
    
    diagnosis = diagnosis_match.group(1).strip() if diagnosis_match else "No diagnosis provided."
    plan = plan_match.group(1).strip() if plan_match else "No plan provided."
    
    file_match = re.search(r'FILE:\s*([\w\.\-/]+)', raw_text)
    filename = file_match.group(1) if file_match else "main.cpp"
    code_match = re.search(r'```(?:html|javascript|cpp|c|python|cuda)?\n(.*?)```', raw_text, re.DOTALL)
    code_content = code_match.group(1).strip() if code_match else None
    
    return filename, diagnosis, plan, code_content

def parse_agent_action(raw_text: str) -> tuple:
    """Parses whether the AI wants to write a file, run a command, or both."""
    bash_match = re.search(r'<bash>(.*?)</bash>', raw_text, re.DOTALL)
    bash_command = bash_match.group(1).strip() if bash_match else None
    
    diagnosis_match = re.search(r'<diagnosis>(.*?)</diagnosis>', raw_text, re.DOTALL)
    plan_match = re.search(r'<plan>(.*?)</plan>', raw_text, re.DOTALL)
    diagnosis = diagnosis_match.group(1).strip() if diagnosis_match else None
    plan = plan_match.group(1).strip() if plan_match else None
    
    file_match = re.search(r'FILE:\s*([\w\.\-/]+)', raw_text)
    filename = file_match.group(1) if file_match else None
    
    code_match = re.search(r'```(?:html|javascript|cpp|c|python|cuda)?\n(.*?)```', raw_text, re.DOTALL)
    code_content = code_match.group(1).strip() if code_match else None
    
    return bash_command, filename, diagnosis, plan, code_content


@router.websocket("/ws/engineer")
async def ai_engineer_loop(websocket: WebSocket):
    await websocket.accept()
    query_params = dict(websocket.query_params)
    session_id = query_params.get("session_id", "default_session")
    
    workspace = Workspace(session_id)
    
    # Standardize path retrieval (handles variations in property naming)
    workspace_path = getattr(workspace, "source_path", getattr(workspace, "workspace_path", None))
    
    # Start live file system watcher
    watcher = DirectoryWatcher(workspace_path, websocket)
    watcher.start()
    
    # Initialize the zero-bloat python sandbox
    sandbox = DockerSandbox(workspace_path, session_id)
    success, msg = sandbox.start()
    if not success:
        await websocket.send_text(json.dumps({"stderr": f"[FATAL] {msg}"}))
        watcher.stop()
        return

    ai = AIEngine(model_name="qwen3:8b")
    
    try:
        while True:
            raw_data = await websocket.receive_text()
            data = json.loads(raw_data)
            
            # Support both 'task' and 'prompt' keys depending on client implementation
            task = data.get("task", data.get("prompt", ""))
            
            if not task:
                continue

            await websocket.send_text(json.dumps({
                "command": f"dispatching agent: \"{task}\"",
                "status_update": "INDEXING"
            }))

            # 1. Scan current host environment & workspace tree
            env_context = EnvironmentScanner.get_context(workspace_path)

            # 2. Build repository context
            repo_context = ContextLoader.build_repository_context(workspace_path)

            # 3. Construct Cursor/Claude-style Agentic System Prompt
            system_prompt = f"""
{env_context}

REPOSITORY CONTEXT:
{repo_context}

SYSTEM INSTRUCTIONS:
You are an expert autonomous software engineer running in a secure local workspace.
Organize your project into clean directories (e.g., `src/`, `include/`, `docs/`, `js/`).
Always include a comprehensive `README.md` and appropriate architecture/plan documentation.

SYSTEM DIRECTIVES:
1. When generating code files, prefix each file with `FILE: path/to/file.ext`.
2. Output clean, zero-bloat, production-ready code inside standard markdown blocks.
3. After generating all files for a project, emit the exact single shell command needed to build and run the project inside <command> tags.
   - Example C++: <command>g++ -O3 -Iinclude src/*.cpp -o app && ./app</command>
   - Example Python: <command>python main.py</command>
   - Example Rust: <command>cargo run</command>
4. If the project is an interactive HTML/WebGL browser app, simply emit: <preview/>

User Goal: {task}
"""

            raw_response = ai.query(system_prompt)
            
            # Parse responses
            bash_match = re.search(r'<bash>(.*?)</bash>', raw_response, re.DOTALL)
            file_match = re.search(r'FILE:\s*([\w\.\-/]+)', raw_response)
            code_match = re.search(r'```(?:html|javascript|cpp|c|python|cuda)?\n(.*?)```', raw_response, re.DOTALL)
            
            bash_command = bash_match.group(1).strip() if bash_match else None
            filename = file_match.group(1).strip() if file_match else "main.cpp"
            code_content = code_match.group(1).strip() if code_match else None

            # Execute Bash via MicroSandbox
            if bash_command:
                await websocket.send_text(json.dumps({
                    "stdout": f"\n$ {bash_command}\n",
                    "status_update": "EXECUTING"
                }))
                await sandbox.execute_bash_streaming(bash_command, websocket)

            # 1. Write incoming file updates quietly as they stream in
            if code_content:
                await workspace.write_file(filename, code_content)
                await websocket.send_text(json.dumps({
                    "code_update": {"filename": filename, "content": code_content},
                    "stdout": f"✔ Deployed file: {filename}\n"
                }))

            # 2. AFTER the AI finishes streaming all files for the task turn:
            await websocket.send_text(json.dumps({"status_update": "BUILDING"}))
            
            # Check if AI explicitly dictated how to build/run, otherwise fallback to heuristics
            if "<command>" in raw_response or "<preview/>" in raw_response:
                await sandbox.run_ai_directive(raw_response, websocket)
            else:
                await sandbox.auto_build_workspace(websocket)
            
    except WebSocketDisconnect:
        watcher.stop()
        sandbox.terminate()
        print("Session disconnected. Workspace cleaned.")
