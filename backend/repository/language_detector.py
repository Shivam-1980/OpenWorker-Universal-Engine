"""
OpenWorker Language Detector
Maps file extensions to programming languages deterministically.
"""

from typing import List
from backend.repository.models import FileNode, LanguageProfile

EXTENSION_MAP = {
    ".cpp": "C++", ".hpp": "C++", ".cc": "C++", ".c": "C", ".h": "C",
    ".py": "Python", ".js": "JavaScript", ".ts": "TypeScript",
    ".rs": "Rust", ".go": "Go", ".java": "Java", ".cs": "C#",
    ".html": "HTML", ".css": "CSS", ".json": "JSON", ".md": "Markdown"
}

class LanguageDetector:
    @staticmethod
    def detect(files: List[FileNode]) -> LanguageProfile:
        breakdown = {}
        for f in files:
            lang = EXTENSION_MAP.get(f.extension, "Unknown")
            if lang != "Unknown":
                breakdown[lang] = breakdown.get(lang, 0) + 1
                
        if not breakdown:
            return LanguageProfile(primary_language="Unknown", breakdown={})
            
        primary = max(breakdown.items(), key=lambda x: x[1])[0]
        return LanguageProfile(primary_language=primary, breakdown=breakdown)
