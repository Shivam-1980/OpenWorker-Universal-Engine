"""
OpenWorker Repository Scanner
Recursively indexes the workspace while ignoring known bloat.
"""

import os
from pathlib import Path
from typing import List
from backend.repository.models import FileNode

IGNORE_DIRS = {".git", "node_modules", "build", "dist", ".venv", "__pycache__", ".idea", ".vscode"}

class RepositoryScanner:
    @staticmethod
    def scan(root_path: Path) -> List[FileNode]:
        nodes = []
        for root, dirs, files in os.walk(root_path):
            # Modify dirs in-place to skip ignored directories
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
            
            for file in files:
                file_path = Path(root) / file
                try:
                    rel_path = file_path.relative_to(root_path).as_posix()
                    nodes.append(FileNode(
                        path=rel_path,
                        name=file_path.name,
                        extension=file_path.suffix.lower(),
                        size_bytes=file_path.stat().st_size,
                        is_dir=False
                    ))
                except (ValueError, OSError):
                    continue
                    
        return nodes
