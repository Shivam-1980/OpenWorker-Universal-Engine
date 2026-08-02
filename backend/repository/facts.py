"""
OpenWorker Engineering Fact Engine
Evaluates raw metrics against engineering thresholds to generate objective facts.
"""

from typing import Dict, List
from backend.repository.models import FileMetrics, EngineeringFact

class FactEngine:
    # Deterministic thresholds
    LARGE_FILE_THRESHOLD = 300  # Lines of code
    HIGH_COUPLING_THRESHOLD = 15  # Number of imports/includes

    @staticmethod
    def evaluate(metrics_map: Dict[str, FileMetrics]) -> List[EngineeringFact]:
        facts = []
        
        for path, metrics in metrics_map.items():
            if metrics.lines_of_code > FactEngine.LARGE_FILE_THRESHOLD:
                facts.append(EngineeringFact(
                    file_path=path, 
                    issue="LARGE_FILE", 
                    severity="MEDIUM", 
                    evidence=f"{metrics.lines_of_code} lines of code."
                ))
                
            if metrics.dependencies > FactEngine.HIGH_COUPLING_THRESHOLD:
                facts.append(EngineeringFact(
                    file_path=path, 
                    issue="HIGH_COUPLING", 
                    severity="HIGH", 
                    evidence=f"{metrics.dependencies} imported dependencies."
                ))
                
        return facts
