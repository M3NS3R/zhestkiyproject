"""Клиент для работы с API ГТУ"""

import requests
from typing import Optional, Dict, Any, List
from datetime import datetime


class GTUApiClient:
    """Клиент для взаимодействия с сервером ГТУ"""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.token: Optional[str] = None
        self.username: Optional[str] = None
    
    def login(self, username: str, password: str) -> bool:
        """Аутентификация на сервере"""
        try:
            response = requests.post(
                f"{self.base_url}/api/login",
                json={"username": username, "password": password}
            )
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("token")
                self.username = data.get("username")
                return True
            return False
        except requests.exceptions.ConnectionError:
            return False
    
    def _get_headers(self) -> Dict[str, str]:
        """Получение заголовков с токеном"""
        return {"Authorization": f"Bearer {self.token}"} if self.token else {}
    
    def get_current_data(self) -> Optional[Dict[str, Any]]:
        """Получение текущих показаний"""
        try:
            response = requests.get(
                f"{self.base_url}/api/current",
                headers=self._get_headers()
            )
            if response.status_code == 200:
                return response.json()
            return None
        except requests.exceptions.ConnectionError:
            return None
    
    def get_history(self, count: int = 100, mode: str = None) -> List[Dict[str, Any]]:
        """Получение истории"""
        try:
            url = f"{self.base_url}/api/history?count={count}"
            if mode:
                url += f"&mode={mode}"
            response = requests.get(url, headers=self._get_headers())
            if response.status_code == 200:
                return response.json().get("history", [])
            return []
        except requests.exceptions.ConnectionError:
            return []
    
    def get_anomalies(self, count: int = 100) -> List[Dict[str, Any]]:
        """Получение аномалий"""
        try:
            response = requests.get(
                f"{self.base_url}/api/anomalies?count={count}",
                headers=self._get_headers()
            )
            if response.status_code == 200:
                return response.json().get("anomalies", [])
            return []
        except requests.exceptions.ConnectionError:
            return []
    
    def set_mode(self, mode: str) -> bool:
        """Установка режима ГТУ"""
        try:
            response = requests.post(
                f"{self.base_url}/api/mode",
                json={"mode": mode},
                headers=self._get_headers()
            )
            return response.status_code == 200
        except requests.exceptions.ConnectionError:
            return False
    
    def get_modes(self) -> List[str]:
        """Получение списка режимов"""
        try:
            response = requests.get(
                f"{self.base_url}/api/modes",
                headers=self._get_headers()
            )
            if response.status_code == 200:
                return response.json().get("modes", [])
            return []
        except requests.exceptions.ConnectionError:
            return []
    
    def is_connected(self) -> bool:
        """Проверка подключения к серверу"""
        try:
            response = requests.get(f"{self.base_url}/api/health")
            return response.status_code == 200
        except requests.exceptions.ConnectionError:
            return False