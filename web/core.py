# web/core.py

import requests
import json
import os
from pathlib import Path
from web.prompts import SYSTEM_ENGINEER_PROMPT, COMPILER_DIAGNOSTIC_PROMPT

OLLAMA_URL = "http://localhost:11434/api/generate"

class AIEngine:
    def __init__(self, model_name="qwen3:8b"):
        self.model_name = model_name

    def query(self, prompt: str, system_override: str = None) -> str:
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "system": system_override or SYSTEM_ENGINEER_PROMPT,
            "stream": False
        }
        try:
            res = requests.post(OLLAMA_URL, json=payload)
            res.raise_for_status()
            return res.json().get("response", "")
        except Exception as e:
            return f"Ollama Error: {str(e)}"

    def diagnose_and_fix(self, error_log: str, code_context: str) -> str:
        prompt = COMPILER_DIAGNOSTIC_PROMPT.format(
            error_log=error_log,
            code_context=code_context
        )
        return self.query(prompt)

class WorkspaceManager:
    def __init__(self, base_dir="./workspace"):
        self.base_dir = Path(base_dir).resolve()
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def write_file(self, relative_path: str, content: str) -> str:
        file_path = self.base_dir / relative_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")
        return str(file_path)

    def read_file(self, relative_path: str) -> str:
        file_path = self.base_dir / relative_path
        if file_path.exists():
            return file_path.read_text(encoding="utf-8")
        return ""

    def list_files(self) -> list:
        files = []
        for path in self.base_dir.rglob("*"):
            if path.is_file():
                files.append(str(path.relative_to(self.base_dir)))
        return files
