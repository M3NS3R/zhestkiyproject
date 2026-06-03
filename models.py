"""Модели данных"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, Any, Optional


@dataclass
class GTUReading:
    """Показания датчиков ГТУ"""
    timestamp: float
    rpm: float
    exhaust_temp: float
    inlet_pressure: float
    fuel_flow: float
    vibration: float
    iga_position: float
    mode: str = "UNKNOWN"
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GTUReading":
        return cls(**data)


@dataclass
class AnomalyRecord:
    """Запись об аномалии"""
    timestamp: float
    mode: str
    parameter: str
    value: float
    min_normal: float
    max_normal: float
    severity: str  # "WARNING" или "CRITICAL"
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AnalysisResult:
    """Результат анализа"""
    timestamp: float
    mode: str
    anomalies: list[AnomalyRecord]
    is_healthy: bool
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "mode": self.mode,
            "anomalies": [a.to_dict() for a in self.anomalies],
            "is_healthy": self.is_healthy,
        }