import time
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class ModelMetadata(BaseModel):
    model_id: str
    model_version: str
    feature_version: str
    dataset_version: str
    training_period: str
    validation_period: str
    algorithm: str
    hyperparameters: Dict[str, Any]
    calibration_method: str
    conformal_method: str
    metrics: Dict[str, float]  # OOS Accuracy, ROC-AUC, Brier score, Conformal Coverage
    evaluation_suite: Optional[Dict[str, Any]] = None  # Per-model ROC curves, confusion matrices, detailed metrics
    training_timestamp: float = Field(default_factory=time.time)
    data_source: str = "YFinance Data Fabric"
    status: str = "CHAMPION"  # CANDIDATE | VALIDATING | CHAMPION | RETIRED | ROLLED_BACK


class InstitutionalModelRegistry:
    """
    Versioned Model Registry for ORION-Q.
    Tracks model lineage, out-of-sample performance, calibration quality, ROC curves, confusion matrices, and status transitions.
    """
    def __init__(self):
        self._registry: Dict[str, List[ModelMetadata]] = {}

    def register_model(self, symbol: str, metadata: ModelMetadata) -> ModelMetadata:
        symbol_clean = symbol.upper().strip()
        if symbol_clean not in self._registry:
            self._registry[symbol_clean] = []
        
        # Demote existing CHAMPION to RETIRED if registering a new CHAMPION
        if metadata.status == "CHAMPION":
            for existing in self._registry[symbol_clean]:
                if existing.status == "CHAMPION":
                    existing.status = "RETIRED"

        self._registry[symbol_clean].append(metadata)
        return metadata

    def get_champion(self, symbol: str) -> Optional[ModelMetadata]:
        symbol_clean = symbol.upper().strip()
        models = self._registry.get(symbol_clean, [])
        for m in reversed(models):
            if m.status == "CHAMPION":
                return m
        return models[-1] if models else None

    def get_history(self, symbol: str) -> List[ModelMetadata]:
        symbol_clean = symbol.upper().strip()
        return self._registry.get(symbol_clean, [])

    def get_all_champions(self) -> Dict[str, ModelMetadata]:
        champions = {}
        for symbol, models in self._registry.items():
            for m in reversed(models):
                if m.status == "CHAMPION":
                    champions[symbol] = m
                    break
        return champions


model_registry = InstitutionalModelRegistry()
