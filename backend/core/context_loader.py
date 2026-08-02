from pathlib import Path

class ContextLoader:
    @staticmethod
    def build_repository_context(workspace_path: Path) -> str:
        """Scans the workspace and compiles a map of all files and their contents."""
        repo_summary = "CURRENT REPOSITORY STRUCTURE & FILES:\n"
        
        if not workspace_path.exists():
            return "Repository is empty."

        for path in workspace_path.rglob("*"):
            if path.is_file() and not ".git" in path.parts:
                rel_path = path.relative_to(workspace_path)
                repo_summary += f"\n--- FILE: {rel_path} ---\n"
                try:
                    content = path.read_text(encoding='utf-8', errors='ignore')
                    # Truncate large files if necessary to protect token limits
                    if len(content) > 4000:
                        content = content[:4000] + "\n[... truncated ...]"
                    repo_summary += content + "\n"
                except Exception as e:
                    repo_summary += f"[Could not read file: {e}]\n"
                    
        return repo_summary
