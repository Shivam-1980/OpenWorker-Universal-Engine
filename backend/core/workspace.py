import shutil
from pathlib import Path
import asyncio

class SecurityError(Exception):
    """Raised when an operation attempts to break out of the workspace sandbox[cite: 4]."""
    pass

class Workspace:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.workspace_path = Path(f"workspaces/{session_id}").resolve()
        self.workspace_path.mkdir(parents=True, exist_ok=True)

    async def write_file(self, relative_filepath: str, content: str):
        """Writes content to a file, automatically creating any nested subdirectories[cite: 4]."""
        target_path = (self.workspace_path / relative_filepath).resolve()
        
        # Prevent path traversal outside workspace using the SecurityError[cite: 4]
        if not str(target_path).startswith(str(self.workspace_path)):
            raise SecurityError(f"Attempted path traversal outside workspace: {relative_filepath}")
            
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Async-safe file writing[cite: 4]
        def _write():
            target_path.write_text(content, encoding="utf-8")
            
        # Python 3.8 compatible background thread execution
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, _write)
        return target_path

    async def get_tree_map(self) -> list:
        """Returns normalized relative file paths for the frontend Explorer[cite: 4]."""
        if not self.workspace_path.exists():
            return []
            
        files = [
            str(p.relative_to(self.workspace_path)).replace("\\", "/")
            for p in self.workspace_path.rglob("*") if p.is_file()
        ]
        return sorted(files)

    async def compress_workspace(self) -> Path:
        """Bundles the entire workspace into a downloadable ZIP archive[cite: 4]."""
        exports_dir = Path("exports").resolve()
        exports_dir.mkdir(parents=True, exist_ok=True)
        
        zip_base_name = exports_dir / f"openworker_{self.session_id}"
        
        def _zip():
            return shutil.make_archive(
                base_name=str(zip_base_name),
                format="zip",
                root_dir=str(self.workspace_path)
            )
            
        # Python 3.8 compatible background thread execution
        loop = asyncio.get_running_loop()
        archive_path = await loop.run_in_executor(None, _zip)
        return Path(archive_path)
