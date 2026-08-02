"""
Utility for generating mock C++ workspace repositories.
"""

import tempfile
import zipfile
from pathlib import Path

def create_dummy_project_zip() -> Path:
    zip_path = Path(tempfile.gettempdir()) / "dummy_project.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("README.md", "# Dummy Renderer\nTesting repository analysis.")
        zf.writestr(
            "CMakeLists.txt",
            "cmake_minimum_required(VERSION 3.16)\nproject(OpenWorkerTest)\nadd_executable(test src/main.cpp src/Renderer.cpp)"
        )
        zf.writestr(
            "src/main.cpp",
            '#include "Renderer.h"\n\nint main() {\n    Renderer renderer;\n    renderer.render();\n    return 0;\n}'
        )
        zf.writestr("src/Renderer.h", "#pragma once\n\nclass Renderer {\npublic:\n    void render();\n};")
        zf.writestr(
            "src/Renderer.cpp",
            '#include "Renderer.h"\n#include <iostream>\n\nvoid Renderer::render() {\n    std::cout << "Rendering..." << std::endl;\n}'
        )
    return zip_path
