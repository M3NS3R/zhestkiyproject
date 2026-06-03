"""Тесты для хранилища данных"""

import pytest
import time
from server.storage import InMemoryStorage
from server.models import GTUReading, AnalysisResult


class TestInMemoryStorage:
    
    def setup_method(self):
        self.storage = InMemoryStorage(max_size=10)
    
    def test_save_and_retrieve(self):
        """Тест сохранения и получения данных"""
        reading = GTUReading(
            timestamp=time.time(),
            rpm=8000,
            exhaust_temp=650,
            inlet_pressure=150,
            fuel_flow=2000,
            vibration=4.0,
            iga_position=99,
            mode="NOMINAL"
        )
        result = AnalysisResult(
            timestamp=reading.timestamp,
            mode="NOMINAL",
            anomalies=[],
            is_healthy=True
        )
        
        self.storage.save(reading, result)
        
        readings = self.storage.get_recent_readings(1)
        results = self.storage.get_recent_results(1)
        
        assert len(readings) == 1
        assert len(results) == 1
        assert readings[0].rpm == 8000
    
    def test_max_size_limit(self):
        """Тест ограничения размера хранилища"""
        for i in range(15):
            reading = GTUReading(
                timestamp=time.time(),
                rpm=8000 + i,
                exhaust_temp=650,
                inlet_pressure=150,
                fuel_flow=2000,
                vibration=4.0,
                iga_position=99,
                mode="NOMINAL"
            )
            result = AnalysisResult(
                timestamp=reading.timestamp,
                mode="NOMINAL",
                anomalies=[],
                is_healthy=True
            )
            self.storage.save(reading, result)
        
        readings = self.storage.get_recent_readings(20)
        assert len(readings) == 10  # max_size=10
    
    def test_history_by_mode(self):
        """Тест фильтрации по режиму"""
        for mode in ["NOMINAL", "PARTIAL", "NOMINAL", "IDLE"]:
            reading = GTUReading(
                timestamp=time.time(),
                rpm=8000,
                exhaust_temp=650,
                inlet_pressure=150,
                fuel_flow=2000,
                vibration=4.0,
                iga_position=99,
                mode=mode
            )
            result = AnalysisResult(
                timestamp=reading.timestamp,
                mode=mode,
                anomalies=[],
                is_healthy=True
            )
            self.storage.save(reading, result)
        
        nominal_history = self.storage.get_history_by_mode("NOMINAL", 10)
        assert len(nominal_history) == 2