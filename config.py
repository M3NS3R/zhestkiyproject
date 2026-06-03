"""Конфигурационный модуль"""

import os
from enum import Enum


class Mode(Enum):
    STOP = "STOP"
    START = "START"
    IDLE = "IDLE"
    PARTIAL = "PARTIAL"
    NOMINAL = "NOMINAL"
    EMERGENCY = "EMERGENCY"


# Нормы для каждого режима (из приложения 2)
NORMAL_RANGES = {
    Mode.STOP: {
        "rpm": (0, 0),
        "exhaust_temp": (16.5, 28.5),
        "inlet_pressure": (100.2, 101.8),
        "fuel_flow": (0, 0),
        "vibration": (0.02, 0.18),
        "iga_position": (0, 0),
    },
    Mode.START: {
        "rpm": (300, 2700),
        "exhaust_temp": (58, 362),
        "inlet_pressure": (102, 118),
        "fuel_flow": (50, 450),
        "vibration": (0.65, 1.85),
        "iga_position": (10, 90),
    },
    Mode.IDLE: {
        "rpm": (2920, 3080),
        "exhaust_temp": (384, 416),
        "inlet_pressure": (116, 124),
        "fuel_flow": (484, 516),
        "vibration": (1.85, 2.25),
        "iga_position": (18.4, 21.6),
    },
    Mode.PARTIAL: {
        "rpm": (4300, 6700),
        "exhaust_temp": (420, 580),
        "inlet_pressure": (122, 138),
        "fuel_flow": (600, 1400),
        "vibration": (2.2, 3.8),
        "iga_position": (26, 74),
    },
    Mode.NOMINAL: {
        "rpm": (7840, 8160),
        "exhaust_temp": (634, 666),
        "inlet_pressure": (148.4, 151.6),
        "fuel_flow": (1960, 2040),
        "vibration": (3.85, 4.25),
        "iga_position": (98.2, 99.8),
    },
    Mode.EMERGENCY: {
        "rpm": (8000, 8500),
        "exhaust_temp": (750, 820),
        "inlet_pressure": (130, 150),
        "fuel_flow": (2300, 2700),
        "vibration": (7.0, 10.0),
        "iga_position": (95, 100),
    },
}

# Параметры для симуляции датчиков (на основе приложения 1)
SIMULATION_PARAMS = {
    Mode.STOP: {
        "rpm": (0, 0, 0, 0),
        "exhaust_temp": (20, 15, 30, 1.0),
        "inlet_pressure": (101.3, 100, 102, 0.5),
        "fuel_flow": (0, 0, 0, 0),
        "vibration": (0, 0, 0.2, 0.05),
        "iga_position": (0, 0, 0, 0),
    },
    Mode.START: {
        "rpm": (1500, 300, 2700, 50),
        "exhaust_temp": (200, 58, 362, 15),
        "inlet_pressure": (110, 102, 118, 1.0),
        "fuel_flow": (250, 50, 450, 20),
        "vibration": (1.0, 0.65, 1.85, 0.1),
        "iga_position": (50, 10, 90, 5),
    },
    Mode.IDLE: {
        "rpm": (3000, 2920, 3080, 20),
        "exhaust_temp": (400, 384, 416, 8),
        "inlet_pressure": (120, 116, 124, 1.0),
        "fuel_flow": (500, 484, 516, 10),
        "vibration": (2.0, 1.85, 2.25, 0.1),
        "iga_position": (20, 18.4, 21.6, 1),
    },
    Mode.PARTIAL: {
        "rpm": (5500, 4300, 6700, 100),
        "exhaust_temp": (500, 420, 580, 20),
        "inlet_pressure": (130, 122, 138, 2),
        "fuel_flow": (1000, 600, 1400, 50),
        "vibration": (3.0, 2.2, 3.8, 0.2),
        "iga_position": (50, 26, 74, 3),
    },
    Mode.NOMINAL: {
        "rpm": (8000, 7840, 8160, 30),
        "exhaust_temp": (650, 634, 666, 10),
        "inlet_pressure": (150, 148.4, 151.6, 1),
        "fuel_flow": (2000, 1960, 2040, 30),
        "vibration": (4.0, 3.85, 4.25, 0.1),
        "iga_position": (99, 98.2, 99.8, 0.5),
    },
    Mode.EMERGENCY: {
        "rpm": (8200, 8000, 8500, 50),
        "exhaust_temp": (780, 750, 820, 15),
        "inlet_pressure": (140, 130, 150, 3),
        "fuel_flow": (2500, 2300, 2700, 100),
        "vibration": (8.5, 7.0, 10.0, 0.5),
        "iga_position": (100, 95, 100, 2),
    },
}

# Секретный ключ для JWT (в реальном проекте - в переменных окружения)
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Настройки БД
DATABASE_URL = "sqlite:///gtu_data.db"

# Пользователи (в реальном проекте - в БД с хэшами)
USERS = {
    "operator": "1489",
    "admin": "admin456",
}