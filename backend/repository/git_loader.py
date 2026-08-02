"""
OpenWorker GitHub Repository Loader
Clones remote GitHub repositories directly into the active session workspace.
"""

import subprocess
import shutil
from pathlib import Path

class GitLoader:
    @staticmethod
    def clone_repository(repo_url: str, target_dir: Path) -> bool:
        if target_dir.exists():
            shutil.rmtree(target_dir)
        target_dir.mkdir(parents=True, exist_ok=True)

        try:
            # Perform a shallow clone to minimize download time and bandwidth
            result = subprocess.run(
                ["git", "clone", "--depth", "1", repo_url, str(target_dir)],
                captureOutput=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                raise RuntimeError(f"Git clone failed: {result.stderr.strip()}")

            # Remove .git folder so the agent focuses purely on source manipulation
            git_meta = target_dir / ".git"
            if git_meta.exists():
                shutil.rmtree(git_meta, ignore_errors=True)

            return True

        except Exception as e:
            print(f"❌ Git Ingestion Error: {str(e)}")
            return False
