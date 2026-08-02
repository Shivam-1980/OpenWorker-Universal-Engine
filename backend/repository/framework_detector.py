"""
OpenWorker Framework Detector
Identifies frameworks based on deterministic file signatures.
"""

from typing import List
from backend.repository.models import FileNode, FrameworkProfile

FRAMEWORK_SIGNATURES = {
    "package.json": ["Node.js"],
    "next.config.js": ["Next.js"],
    "manage.py": ["Django"],
    "fastapi": ["FastAPI"],  # Usually requires reading requirements.txt, simplified for now
    "pom.xml": ["Spring Boot"],
}

class FrameworkDetector:
    @staticmethod
    def detect(files: List[FileNode]) -> FrameworkProfile:
        frameworks = set()
        file_names = {f.name for f in files}
        
        for sig, fw_list in FRAMEWORK_SIGNATURES.items():
            if sig in file_names:
                frameworks.update(fw_list)
                
        return FrameworkProfile(detected_frameworks=list(frameworks))
