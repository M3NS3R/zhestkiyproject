"""Сервис опроса датчиков (симуляция АСУТП)"""

import random
import time
from typing import Optional
from server.config import SIMULATION_PARAMS, Mode
from server.models import GTUReading
from server.logger import GTULogger


class DataAcquisitionService:
    """Сервис опроса датчиков"""
    
    def __init__(self):
        self._current_mode = Mode.STOP
        self.logger = GTULogger()
    
    def set_mode(self, mode: Mode):
        """Установка текущего режима ГТУ"""
        self._current_mode = mode
        self.logger.info(f"Режим ГТУ изменен на: {mode.value}")
    
    def get_current_mode(self) -> Mode:
        """Получение текущего режима"""
        return self._current_mode
    
    def _generate_value(self, mean: float, min_val: float, max_val: float, sigma: float) -> float:
        """Генерация значения с нормальным распределением"""
        if sigma == 0:
            return mean
        val = random.gauss(mean, sigma)
        return max(min_val, min(max_val, val))
    
    def get_reading(self) -> Optional[GTUReading]:
        """Получение текущих показаний"""
        params = SIMULATION_PARAMS.get(self._current_mode)
        if not params:
            return None
        
        try:
            rpm = self._generate_value(*params["rpm"])
            exhaust_temp = self._generate_value(*params["exhaust_temp"])
            inlet_pressure = self._generate_value(*params["inlet_pressure"])
            fuel_flow = self._generate_value(*params["fuel_flow"])
            vibration = self._generate_value(*params["vibration"])
            iga_position = self._generate_value(*params["iga_position"])
            
            return GTUReading(
                timestamp=time.time(),
                rpm=round(rpm, 2),
                exhaust_temp=round(exhaust_temp, 2),
                inlet_pressure=round(inlet_pressure, 2),
                fuel_flow=round(fuel_flow, 2),
                vibration=round(vibration, 2),
                iga_position=round(iga_position, 2),
                mode=self._current_mode.value,
            )
        except Exception as e:
            self.logger.error(f"Ошибка получения показаний: {e}")
            return None