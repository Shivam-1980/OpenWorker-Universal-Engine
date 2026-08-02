"""
OpenWorker Build System Detector
Identifies build orchestrators.
"""

from typing import List
from backend.repository.models import FileNode, BuildProfile

BUILD_SIGNATURES = {
    "CMakeLists.txt": "CMake",
    "Makefile": "Make",
    "Cargo.toml": "Cargo",
    "package.json": "npm/yarn",
    "requirements.txt": "pip",
    "pyproject.toml": "Poetry/pip",
    "build.gradle": "Gradle",
}

class BuildDetector:
    @staticmethod
    def detect(files: List[FileNode]) -> BuildProfile:
        build_systems = set()
        file_names = {f.name for f in files}
        
        for sig, sys_name in BUILD_SIGNATURES.items():
            if sig in file_names:
                build_systems.add(sys_name)
                
        return BuildProfile(build_systems=list(build_systems))
