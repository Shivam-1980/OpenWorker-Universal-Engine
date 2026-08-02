"""
OpenWorker RepoMap Engine
Generates a high-density, token-efficient symbol map of the codebase.
"""

import re
from pathlib import Path
from typing import List
from backend.repository.models import FileNode

# Regex pattern for class/struct definitions, function signatures, and header includes
SYMBOL_PATTERN = re.compile(
    r'^\s*(#include\s+["<][^">]+[">]|class\s+\w+|struct\s+\w+|def\s+\w+|[\w:<>]+\s+\w+\s*\(.*?\)\s*[{;]?)',
    re.MULTILINE
)

class RepoMapGenerator:
    @staticmethod
    def generate(workspace_src_path: Path, files: List[FileNode]) -> str:
        map_lines = []
        
        for f in files:
            if f.extension not in {".h", ".hpp", ".cpp", ".c", ".cc", ".py"}:
                continue
                
            target_path = workspace_src_path / f.path
            try:
                with open(target_path, "r", encoding="utf-8") as file:
                    content = file.read()
                    
                symbols = SYMBOL_PATTERN.findall(content)
                if symbols:
                    map_lines.append(f"📄 {f.path}:")
                    for sym in symbols:
                        cleaned = sym.strip().rstrip('{').strip()
                        map_lines.append(f"   ├─ {cleaned}")
            except UnicodeDecodeError:
                continue
                
        return "\n".join(map_lines)
