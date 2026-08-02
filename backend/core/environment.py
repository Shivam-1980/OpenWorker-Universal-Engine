import platform
import shutil
from pathlib import Path

class EnvironmentScanner:
    """Scans the host system toolchains, package managers, and workspace tree."""
    
    @staticmethod
    def get_context(workspace_path: Path) -> str:
        os_name = platform.system()
        
        # Check available toolchains, compilers, and package managers
        tools = [
            "python", "python3", "pip", "pip3", "g++", "gcc", "clang", 
            "nvcc", "node", "npm", "cargo", "go", "cmake", "make", "apt", "bash"
        ]
        available_tools = [t for t in tools if shutil.which(t)]
        
        # Build current relative file tree
        files = []
        if workspace_path.exists():
            files = [
                str(p.relative_to(workspace_path)).replace("\\", "/") 
                for p in workspace_path.rglob("*") if p.is_file()
            ]
        
        file_tree_str = "\n".join([f"  - {f}" for f in files]) if files else "  (Empty Directory)"
        
        return f"""
[HOST & WORKSPACE ENVIRONMENT CONTEXT]
OS Platform: {os_name}
Available CLI Tools & Compilers: {', '.join(available_tools) if available_tools else 'Standard Shell'}
Workspace Root: {workspace_path.resolve()}

Existing File Tree:
{file_tree_str}
"""
