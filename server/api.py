"""REST API сервер"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from functools import wraps
from threading import Thread
import time
from typing import Optional

from server.config import Mode
from server.data_acquisition import DataAcquisitionService
from server.analyzer import AnomalyAnalyzer
from server.storage import InMemoryStorage
from server.database import DatabaseManager
from server.auth import AuthService
from server.logger import GTULogger
from server.models import GTUReading


class GTUAPIServer:
    """REST API сервер для ГТУ"""
    
    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app)
        
        # Сервисы
        self.data_acquisition = DataAcquisitionService()
        self.analyzer = AnomalyAnalyzer()
        self.storage = InMemoryStorage()
        self.database = DatabaseManager()
        self.auth = AuthService()
        self.logger = GTULogger()
        
        # Флаг работы
        self._is_running = False
        self._acquisition_thread = None
        
        # Регистрация маршрутов
        self._register_routes()
    
    def _require_auth(self, f):
        """Декоратор для проверки аутентификации"""
        @wraps(f)
        def decorated(*args, **kwargs):
            token = request.headers.get('Authorization', '').replace('Bearer ', '')
            if not self.auth.verify_token(token):
                return jsonify({"error": "Unauthorized"}), 401
            return f(*args, **kwargs)
        return decorated
    
    def _register_routes(self):
        """Регистрация всех API маршрутов"""
        
        @self.app.route('/api/login', methods=['POST'])
        def login():
            data = request.json
            username = data.get('username')
            password = data.get('password')
            token = self.auth.authenticate(username, password)
            if token:
                return jsonify({"token": token, "username": username})
            return jsonify({"error": "Invalid credentials"}), 401
        
        @self.app.route('/api/current', methods=['GET'])
        @self._require_auth
        def get_current():
            reading = self.data_acquisition.get_reading()
            if reading:
                result = self.analyzer.analyze(reading)
                return jsonify({
                    "reading": reading.to_dict(),
                    "analysis": result.to_dict()
                })
            return jsonify({"error": "No data"}), 500
        
        @self.app.route('/api/history', methods=['GET'])
        @self._require_auth
        def get_history():
            count = request.args.get('count', 100, type=int)
            mode = request.args.get('mode', None)
            
            if mode:
                history = self.storage.get_history_by_mode(mode, count)
            else:
                history = [r.to_dict() for r in self.storage.get_recent_readings(count)]
            
            return jsonify({"history": history})
        
        @self.app.route('/api/anomalies', methods=['GET'])
        @self._require_auth
        def get_anomalies():
            count = request.args.get('count', 100, type=int)
            anomalies = self.database.get_anomalies(count)
            return jsonify({
                "anomalies": [
                    {
                        "timestamp": a.timestamp,
                        "mode": a.mode,
                        "parameter": a.parameter,
                        "value": a.value,
                        "min_normal": a.min_normal,
                        "max_normal": a.max_normal,
                        "severity": a.severity,
                    }
                    for a in anomalies
                ]
            })
        
        @self.app.route('/api/mode', methods=['POST'])
        @self._require_auth
        def set_mode():
            data = request.json
            mode_name = data.get('mode')
            try:
                mode = Mode(mode_name)
                self.data_acquisition.set_mode(mode)
                self.logger.info(f"Режим изменен на {mode_name} через API")
                return jsonify({"status": "ok", "mode": mode_name})
            except ValueError:
                return jsonify({"error": "Invalid mode"}), 400
        
        @self.app.route('/api/modes', methods=['GET'])
        @self._require_auth
        def get_modes():
            return jsonify({"modes": [m.value for m in Mode]})
        
        @self.app.route('/api/health', methods=['GET'])
        def health():
            return jsonify({"status": "healthy"})
    
    def _acquisition_loop(self, interval: float = 1.0):
        """Цикл сбора данных"""
        while self._is_running:
            reading = self.data_acquisition.get_reading()
            if reading:
                result = self.analyzer.analyze(reading)
                self.storage.save(reading, result)
                self.database.save_reading(reading, result)
                self.logger.debug(f"Собраны данные: rpm={reading.rpm}")
            time.sleep(interval)
    
    def start(self, host: str = '0.0.0.0', port: int = 5000, acquisition_interval: float = 1.0):
        """Запуск API сервера"""
        self._is_running = True
        self._acquisition_thread = Thread(target=self._acquisition_loop, args=(acquisition_interval,), daemon=True)
        self._acquisition_thread.start()
        
        self.logger.info(f"Запуск API сервера на {host}:{port}")
        self.app.run(host=host, port=port, threaded=True)
    
    def stop(self):
        """Остановка сервера"""
        self._is_running = False
        self.logger.info("Остановка сервера")