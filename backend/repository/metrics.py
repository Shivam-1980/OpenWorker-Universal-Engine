"""
OpenWorker Metrics Extractor
Deterministically calculates raw file metrics (LOC, blank lines, dependencies).
"""

import re
from pathlib import Path
from typing import List, Dict
from backend.repository.models import FileNode, FileMetrics

# Captures C++ #include, Python import/from, JS/TS import
DEPENDENCY_PATTERN = re.compile(r'^\s*(#include|import|from\s+[\w\.]+\s+import)\b')

class MetricsExtractor:
    @staticmethod
    def extract(workspace_src_path: Path, files: List[FileNode]) -> Dict[str, FileMetrics]:
        metrics_map = {}
        
        for f in files:
            target_path = workspace_src_path / f.path
            loc = 0
            blank = 0
            deps = 0
            
            try:
                # Attempt to read as UTF-8. Binary files will throw UnicodeDecodeError and be skipped.
                with open(target_path, 'r', encoding='utf-8') as file:
                    for line in file:
                        loc += 1
                        if not line.strip():
                            blank += 1
                        elif DEPENDENCY_PATTERN.match(line):
                            deps += 1
                            
                metrics_map[f.path] = FileMetrics(
                    lines_of_code=loc, 
                    blank_lines=blank, 
                    dependencies=deps
                )
            except UnicodeDecodeError:
                # Safely ignore binary assets (images, compiled objects, etc.)
                pass
                
        return metrics_map
