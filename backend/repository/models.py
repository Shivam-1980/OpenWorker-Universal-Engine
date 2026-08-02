"""
OpenWorker Repository Models
"""

from typing import List, Dict
from pydantic import BaseModel, Field

class FileNode(BaseModel):
    path: str
    name: str
    extension: str
    size_bytes: int
    is_dir: bool

class LanguageProfile(BaseModel):
    primary_language: str
    breakdown: Dict[str, int]

class FrameworkProfile(BaseModel):
    detected_frameworks: List[str]

class BuildProfile(BaseModel):
    build_systems: List[str]

class FileMetrics(BaseModel):
    lines_of_code: int = 0
    blank_lines: int = 0
    dependencies: int = 0

class EngineeringFact(BaseModel):
    file_path: str
    issue: str
    severity: str
    evidence: str

class RepositoryProfile(BaseModel):
    total_files: int
    total_directories: int
    languages: LanguageProfile
    frameworks: FrameworkProfile
    build_systems: BuildProfile
    metrics: Dict[str, FileMetrics] = Field(default_factory=dict)
    facts: List[EngineeringFact] = Field(default_factory=list)
    repo_map: str = ""
    files: List[FileNode] = Field(exclude=True)
