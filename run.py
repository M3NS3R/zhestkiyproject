#!/usr/bin/env python3
"""Точка входа в приложение"""

import sys
import threading
import signal
from PyQt5.QtWidgets import QApplication

from server.api import GTUAPIServer
from client.main_window import MainWindow


def run_server():
    """Запуск сервера в отдельном потоке"""
    server = GTUAPIServer()
    server.start(host='0.0.0.0', port=5000, acquisition_interval=1.0)


def run_client():
    """Запуск клиентского приложения"""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


def main():
    """Главная функция"""
    print("=" * 50)
    print("Система анализа данных ГТУ")
    print("=" * 50)
    print("Запуск сервера на http://localhost:5000")
    print("Запуск клиентского интерфейса...")
    print("-" * 50)
    
    # Запуск сервера в отдельном потоке
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Запуск клиента в основном потоке
    run_client()


if __name__ == "__main__":
    main()