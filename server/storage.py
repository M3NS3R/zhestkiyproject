"""Хранилище данных с результатами"""

from typing import List, Dict, Any
from collections import deque
from datetime import datetime
from server.models import AnalysisResult, GTUReading
from server.logger import GTULogger


class InMemoryStorage:
    """Хранилище в памяти (для быстрого доступа)"""
    
    def __init__(self, max_size: int = 1000):
        self._readings: deque = deque(maxlen=max_size)
        self._results: deque = deque(maxlen=max_size)
        self.logger = GTULogger()
    
    def save(self, reading: GTUReading, result: AnalysisResult):
        """Сохранение данных"""
        self._readings.append(reading)
        self._results.append(result)
        self.logger.debug(f"Сохранены данные для timestamp={reading.timestamp}")
    
    def get_recent_readings(self, count: int = 100) -> List[GTUReading]:
        """Получение последних показаний"""
        return list(self._readings)[-count:]
    
    def get_recent_results(self, count: int = 100) -> List[AnalysisResult]:
        """Получение последних результатов"""
        return list(self._results)[-count:]
    
    def get_history_by_mode(self, mode: str, count: int = 50) -> List[Dict[str, Any]]:
        """Получение истории по режиму"""
        results = []
        for reading, result in zip(self._readings, self._results):
            if result.mode == mode:
                results.append({
                    "timestamp": reading.timestamp,
                    "datetime": datetime.fromtimestamp(reading.timestamp).strftime("%Y-%m-%d %H:%M:%S"),
                    "rpm": reading.rpm,
                    "exhaust_temp": reading.exhaust_temp,
                    "inlet_pressure": reading.inlet_pressure,
                    "fuel_flow": reading.fuel_flow,
                    "vibration": reading.vibration,
                    "iga_position": reading.iga_position,
                    "is_healthy": result.is_healthy,
                    "anomalies_count": len(result.anomalies),
                })
                if len(results) >= count:
                    break
        return results