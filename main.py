"""
OpenWorker Universal Engine Entrypoint
Supports GitHub repos, local paths, or raw system prompts.
"""

import asyncio
import shutil
import traceback
import uvicorn
from web.server import app
from pathlib import Path
from backend.core.session import Session, SessionStatus
from backend.repository.analyzer import RepositoryAnalyzer
from backend.repository.git_loader import GitLoader
from backend.tools.registry import ToolRegistry
from backend.llm.ollama_client import OllamaClient
from backend.llm.architect import ArchitectAgent
from backend.llm.agent import OpenWorkerAgent
from backend.utils.console_logger import stream_logs_to_console

async def main():
    print("\n🚀 OpenWorker Universal Engine Initializing...\n")
    
    # --- INPUT CONFIGURATION ---
    # Set this to a GitHub URL (e.g., "https://github.com/user/repo.git"),
    # a local path, or None if building entirely from a prompt.
    INPUT_SOURCE = None 
    
    USER_OBJECTIVE = (
        "Design and implement a high-performance C++ Win32 and DirectX 12 rendering framework "
        "from first principles. Include proper device creation, swapchains, command allocators, "
        "and explicit memory management comments. Ensure it compiles cleanly with g++ or MSBuild, "
        "and generate README_CHANGES.md, PLAN.md, and requirements.txt."
    )
    # ---------------------------

    session = Session()
    log_task = asyncio.create_task(stream_logs_to_console(session))

    try:
        # 1. Bootstrap Workspace based on Input Source
        await session.update_status(SessionStatus.INITIALIZED, "Bootstrapping Workspace")
        
        if INPUT_SOURCE and INPUT_SOURCE.startswith("http"):
            print(f"📥 Cloning repository from {INPUT_SOURCE}...")
            success = GitLoader.clone_repository(INPUT_SOURCE, session.workspace.source_path)
            if not success:
                raise RuntimeError(f"Failed to ingest GitHub repository: {INPUT_SOURCE}")
        elif INPUT_SOURCE and Path(INPUT_SOURCE).exists():
            print(f"📂 Copying local project from {INPUT_SOURCE}...")
            shutil.copytree(INPUT_SOURCE, session.workspace.source_path, dirs_exist_ok=True)
        else:
            print("📝 Initializing clean workspace for prompt-driven development...")
            (session.workspace.source_path / "src").mkdir(exist_ok=True)

        # 2. Analyze Repository & Generate Symbol Map
        await session.update_status(SessionStatus.ANALYZING, "Scanning Repository & Mapping Symbols")
        analyzer = RepositoryAnalyzer()
        profile = analyzer.analyze(session.workspace.source_path)

        # 3. Setup LLM Client and Tool Registry
        registry = ToolRegistry()
        client = OllamaClient(model="qwen3:8b")

        # 4. Phase 1: Architect Planning (Drafting PLAN.md)
        await session.update_status(SessionStatus.EXECUTING, "Running Architect Planning Phase")
        architect = ArchitectAgent(session, registry, client)
        plan_success = await architect.draft_plan(
            user_objective=USER_OBJECTIVE,
            repo_profile_json=profile.model_dump_json(exclude={"files"})
        )

        if not plan_success:
            print("⚠️ Architect failed to generate PLAN.md, proceeding with direct execution...")

        # Re-scan profile to include newly created PLAN.md in context
        profile = analyzer.analyze(session.workspace.source_path)

        # 5. Phase 2: Worker Execution (Coding, Testing, Self-Correction)
        await session.update_status(SessionStatus.EXECUTING, "Running OpenWorker Execution Agent")
        worker_agent = OpenWorkerAgent(session, registry, client)
        
        worker_objective = (
            f"{USER_OBJECTIVE}\n\n"
            "Follow the specifications in 'PLAN.md' strictly. "
            "Ensure all code files contain thorough architectural comments explaining your logic. "
            "Verify compilation using BuildAndTest and conclude by creating README_CHANGES.md and requirements.txt."
        )

        await worker_agent.run(
            user_objective=worker_objective,
            repo_profile_json=profile.model_dump_json(exclude={"files"})
        )

        # 6. Export Workspace Package
        await session.update_status(SessionStatus.COMPLETED, "Packaging Workspace")
        temp_export_path = await session.workspace.compress_workspace()

        persistent_export_dir = Path("exports")
        persistent_export_dir.mkdir(exist_ok=True)
        final_export_path = persistent_export_dir / Path(temp_export_path).name
        
        shutil.copy(temp_export_path, final_export_path)
        
        print(f"\n✅ Pipeline Complete. Export persisted at:\n{final_export_path.resolve()}\n")

    except Exception as e:
        print(f"\n❌ Pipeline Failure: {e}")
        print("\n--- Stack Trace ---")
        traceback.print_exc()
    finally:
        await session.workspace.cleanup()
        log_task.cancel()

if __name__ == "__main__":
    asyncio.run(main())
    uvicorn.run("web.server:app",hosts="0.0.0.0",port=8000,reload=True)
