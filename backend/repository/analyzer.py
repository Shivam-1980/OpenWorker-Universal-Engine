"""
OpenWorker Repository Analyzer
"""

from pathlib import Path
from backend.repository.models import RepositoryProfile
from backend.repository.scanner import RepositoryScanner
from backend.repository.language_detector import LanguageDetector
from backend.repository.framework_detector import FrameworkDetector
from backend.repository.build_detector import BuildDetector
from backend.repository.metrics import MetricsExtractor
from backend.repository.facts import FactEngine
from backend.repository.repomap import RepoMapGenerator

class RepositoryAnalyzer:
    @staticmethod
    def analyze(workspace_src_path: Path) -> RepositoryProfile:
        files = RepositoryScanner.scan(workspace_src_path)
        languages = LanguageDetector.detect(files)
        frameworks = FrameworkDetector.detect(files)
        build_systems = BuildDetector.detect(files)
        metrics = MetricsExtractor.extract(workspace_src_path, files)
        facts = FactEngine.evaluate(metrics)
        repo_map = RepoMapGenerator.generate(workspace_src_path, files)
        
        return RepositoryProfile(
            total_files=len(files),
            total_directories=len({Path(f.path).parent for f in files}),
            languages=languages,
            frameworks=frameworks,
            build_systems=build_systems,
            metrics=metrics,
            facts=facts,
            repo_map=repo_map,
            files=files
        )
