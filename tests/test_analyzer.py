"""Тесты для сервиса анализа"""

import pytest
import time
from server.analyzer import AnomalyAnalyzer
from server.models import GTUReading
from server.config import Mode, NORMAL_RANGES


class TestAnomalyAnalyzer:
    
    def setup_method(self):
        self.analyzer = AnomalyAnalyzer()
    
    def test_normal_reading(self):
        """Тест нормальных показаний"""
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
        
        result = self.analyzer.analyze(reading)
        
        assert result.is_healthy is True
        assert len(result.anomalies) == 0
        assert result.mode == "NOMINAL"
    
    def test_anomaly_detection(self):
        """Тест обнаружения аномалии"""
        reading = GTUReading(
            timestamp=time.time(),
            rpm=3000,  # нормальная частота для IDLE
            exhaust_temp=500,  # аномальная температура
            inlet_pressure=120,
            fuel_flow=500,
            vibration=2.0,
            iga_position=20,
            mode="IDLE"
        )
        
        result = self.analyzer.analyze(reading)
        
        assert result.is_healthy is False
        assert len(result.anomalies) == 1
        assert result.anomalies[0].parameter == "exhaust_temp"
    
    def test_stop_mode(self):
        """Тест режима остановки"""
        reading = GTUReading(
            timestamp=time.time(),
            rpm=0,
            exhaust_temp=20,
            inlet_pressure=101.3,
            fuel_flow=0,
            vibration=0.1,
            iga_position=0,
            mode="STOP"
        )
        
        result = self.analyzer.analyze(reading)
        
        normals = NORMAL_RANGES[Mode.STOP]
        assert result.is_healthy is True
        assert len(result.anomalies) == 0
    
    def test_critical_anomaly(self):
        """Тест критической аномалии (большое отклонение)"""
        reading = GTUReading(
            timestamp=time.time(),
            rpm=8000,
            exhaust_temp=800,  # сильно выше нормы
            inlet_pressure=150,
            fuel_flow=2000,
            vibration=12.0,  # сильно выше нормы
            iga_position=99,
            mode="NOMINAL"
        )
        
        result = self.analyzer.analyze(reading)
        
        anomalies = result.anomalies
        assert len(anomalies) == 2
        
        for a in anomalies:
            if a.parameter == "exhaust_temp":
                assert a.severity == "CRITICAL"
            if a.parameter == "vibration":
                assert a.severity == "CRITICAL"
    
    def test_auto_mode_detection(self):
        """Тест автоматического определения режима"""
        reading = GTUReading(
            timestamp=time.time(),
            rpm=5000,  # PARTIAL диапазон
            exhaust_temp=500,
            inlet_pressure=130,
            fuel_flow=1000,
            vibration=3.0,
            iga_position=50,
            mode="UNKNOWN"
        )
        
        result = self.analyzer.analyze(reading)
        
        assert result.mode == "PARTIAL"