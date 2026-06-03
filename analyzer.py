"""Сервис анализа данных и выявления аномалий"""

from typing import List
from server.config import NORMAL_RANGES, Mode
from server.models import GTUReading, AnomalyRecord, AnalysisResult
from server.logger import GTULogger


class AnomalyAnalyzer:
    """Анализатор аномалий (SOLID: Single Responsibility - только анализ)"""
    
    def __init__(self):
        self.logger = GTULogger()
    
    def _check_parameter(self, param_name: str, value: float, mode: Mode) -> AnomalyRecord:
        """Проверка одного параметра на аномалию"""
        ranges = NORMAL_RANGES.get(mode, {})
        if param_name not in ranges:
            return None
        
        min_val, max_val = ranges[param_name]
        
        if value < min_val or value > max_val:
            severity = "CRITICAL" if abs(value - min_val) > 0.2 * min_val or abs(value - max_val) > 0.2 * max_val else "WARNING"
            return AnomalyRecord(
                timestamp=0,  # будет заполнено позже
                mode=mode.value,
                parameter=param_name,
                value=value,
                min_normal=min_val,
                max_normal=max_val,
                severity=severity,
            )
        return None
    
    def analyze(self, reading: GTUReading) -> AnalysisResult:
        """Анализ показаний ГТУ"""
        anomalies: List[AnomalyRecord] = []
        
        # Определяем режим (если еще не определен)
        mode = Mode(reading.mode) if reading.mode != "UNKNOWN" else self._detect_mode(reading)
        
        # Проверяем каждый параметр
        param_names = ["rpm", "exhaust_temp", "inlet_pressure", "fuel_flow", "vibration", "iga_position"]
        
        for param_name in param_names:
            value = getattr(reading, param_name)
            anomaly = self._check_parameter(param_name, value, mode)
            if anomaly:
                anomaly.timestamp = reading.timestamp
                anomalies.append(anomaly)
                self.logger.warning(
                    f"Аномалия: {param_name}={value} вне нормы [{anomaly.min_normal}, {anomaly.max_normal}] "
                    f"в режиме {mode.value} (Severity: {anomaly.severity})"
                )
        
        is_healthy = len(anomalies) == 0
        
        return AnalysisResult(
            timestamp=reading.timestamp,
            mode=mode.value,
            anomalies=anomalies,
            is_healthy=is_healthy,
        )
    
    def _detect_mode(self, reading: GTUReading) -> Mode:
        """Определение режима по показаниям (резервный метод)"""
        rpm = reading.rpm
        
        if rpm == 0:
            return Mode.STOP
        elif rpm < 2900:
            return Mode.START
        elif rpm < 3100:
            return Mode.IDLE
        elif rpm < 6700:
            return Mode.PARTIAL
        elif rpm < 8200:
            return Mode.NOMINAL
        else:
            return Mode.EMERGENCY