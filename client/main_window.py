"""Главное окно приложения PyQt5"""

import sys
from datetime import datetime
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QTableWidget,
    QTableWidgetItem, QTabWidget, QMessageBox, QStatusBar,
    QLineEdit, QDialog, QFormLayout, QDialogButtonBox
)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont

from client.api_client import GTUApiClient
from client.widgets import GaugeWidget, ModeIndicator, AnomalyListWidget
from server.config import NORMAL_RANGES, Mode


class LoginDialog(QDialog):
    """Диалог аутентификации"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Авторизация")
        self.setModal(True)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        form = QFormLayout()
        self.username_edit = QLineEdit()
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        
        form.addRow("Логин:", self.username_edit)
        form.addRow("Пароль:", self.password_edit)
        layout.addLayout(form)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def get_credentials(self):
        return self.username_edit.text(), self.password_edit.text()


class MainWindow(QMainWindow):
    """Главное окно приложения"""
    
    def __init__(self):
        super().__init__()
        self.client = GTUApiClient()
        self.current_mode = Mode.STOP
        self.setWindowTitle("Система анализа данных ГТУ")
        self.setGeometry(100, 100, 1200, 800)
        
        self._setup_ui()
        self._setup_timer()
        self._load_modes()
        self._update_status_message("Ожидание подключения к серверу...")
    
    def _setup_ui(self):
        """Настройка пользовательского интерфейса"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        # Верхняя панель с управлением
        control_panel = QHBoxLayout()
        
        self.mode_combo = QComboBox()
        self.mode_combo.setMinimumWidth(150)
        self.mode_combo.currentTextChanged.connect(self._on_mode_changed)
        control_panel.addWidget(QLabel("Режим ГТУ:"))
        control_panel.addWidget(self.mode_combo)
        
        self.connect_btn = QPushButton("Подключиться")
        self.connect_btn.clicked.connect(self._on_connect)
        control_panel.addWidget(self.connect_btn)
        
        self.login_btn = QPushButton("Войти")
        self.login_btn.clicked.connect(self._on_login)
        control_panel.addWidget(self.login_btn)
        
        self.logout_btn = QPushButton("Выйти")
        self.logout_btn.clicked.connect(self._on_logout)
        self.logout_btn.setEnabled(False)
        control_panel.addWidget(self.logout_btn)
        
        control_panel.addStretch()
        main_layout.addLayout(control_panel)
        
        # Табы
        tabs = QTabWidget()
        
        # Вкладка мониторинга
        monitoring_tab = QWidget()
        monitoring_layout = QHBoxLayout(monitoring_tab)
        
        # Левая панель - индикаторы
        left_panel = QVBoxLayout()
        
        self.mode_indicator = ModeIndicator()
        left_panel.addWidget(self.mode_indicator)
        
        # Сетка с индикаторами
        gauges_layout = QVBoxLayout()
        
        # Верхний ряд индикаторов
        top_gauges = QHBoxLayout()
        self.rpm_gauge = GaugeWidget("Частота вращения", "об/мин", 0, 9000)
        self.temp_gauge = GaugeWidget("Температура выхлопа", "°C", 0, 900)
        self.pressure_gauge = GaugeWidget("Давление на входе", "кПа", 95, 170)
        top_gauges.addWidget(self.rpm_gauge)
        top_gauges.addWidget(self.temp_gauge)
        top_gauges.addWidget(self.pressure_gauge)
        gauges_layout.addLayout(top_gauges)
        
        # Нижний ряд индикаторов
        bottom_gauges = QHBoxLayout()
        self.fuel_gauge = GaugeWidget("Расход топлива", "кг/ч", 0, 3200)
        self.vibro_gauge = GaugeWidget("Вибрация", "мм/с", 0, 13)
        self.iga_gauge = GaugeWidget("Положение IGA", "%", 0, 100)
        bottom_gauges.addWidget(self.fuel_gauge)
        bottom_gauges.addWidget(self.vibro_gauge)
        bottom_gauges.addWidget(self.iga_gauge)
        gauges_layout.addLayout(bottom_gauges)
        
        left_panel.addLayout(gauges_layout)
        
        # Правая панель - аномалии
        right_panel = QVBoxLayout()
        self.anomaly_list = AnomalyListWidget()
        right_panel.addWidget(self.anomaly_list)
        
        monitoring_layout.addLayout(left_panel, 2)
        monitoring_layout.addLayout(right_panel, 1)
        
        # Вкладка истории
        history_tab = QWidget()
        history_layout = QVBoxLayout(history_tab)
        
        history_controls = QHBoxLayout()
        history_controls.addWidget(QLabel("Режим:"))
        self.history_mode_combo = QComboBox()
        history_controls.addWidget(self.history_mode_combo)
        
        self.refresh_history_btn = QPushButton("Обновить")
        self.refresh_history_btn.clicked.connect(self._load_history)
        history_controls.addWidget(self.refresh_history_btn)
        history_controls.addStretch()
        history_layout.addLayout(history_controls)
        
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(8)
        self.history_table.setHorizontalHeaderLabels([
            "Время", "RPM", "T°C", "P кПа", "Топливо кг/ч", "Вибрация мм/с", "IGA %", "Состояние"
        ])
        history_layout.addWidget(self.history_table)
        
        # Вкладка аномалий
        anomalies_tab = QWidget()
        anomalies_layout = QVBoxLayout(anomalies_tab)
        
        anomalies_controls = QHBoxLayout()
        self.refresh_anomalies_btn = QPushButton("Обновить")
        self.refresh_anomalies_btn.clicked.connect(self._load_anomalies)
        anomalies_controls.addStretch()
        anomalies_controls.addWidget(self.refresh_anomalies_btn)
        anomalies_layout.addLayout(anomalies_controls)
        
        self.anomalies_table = QTableWidget()
        self.anomalies_table.setColumnCount(6)
        self.anomalies_table.setHorizontalHeaderLabels([
            "Время", "Режим", "Параметр", "Значение", "Норма", "Severity"
        ])
        anomalies_layout.addWidget(self.anomalies_table)
        
        tabs.addTab(monitoring_tab, "Мониторинг")
        tabs.addTab(history_tab, "История")
        tabs.addTab(anomalies_tab, "Журнал аномалий")
        
        main_layout.addWidget(tabs)
        
        # Статус бар - создаем и сохраняем как отдельный атрибут
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_label = QLabel("Не авторизован")
        self.status_bar.addWidget(self.status_label)
    
    def _update_status_message(self, message: str, timeout: int = 0):
        """Обновление сообщения в статус-баре"""
        if hasattr(self, 'status_bar'):
            self.status_bar.showMessage(message, timeout)
    
    def _setup_timer(self):
        """Настройка таймера обновления данных"""
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_data)
        self.timer.start(1000)  # 1 секунда
    
    def _load_modes(self):
        """Загрузка списка режимов"""
        modes = [m.value for m in Mode]
        self.mode_combo.addItems(modes)
        self.history_mode_combo.addItem("Все")
        self.history_mode_combo.addItems(modes)
    
    def _on_connect(self):
        """Подключение к серверу"""
        if self.client.is_connected():
            QMessageBox.information(self, "Подключение", "Сервер доступен")
            self._update_status_message("Сервер доступен", 3000)
        else:
            QMessageBox.warning(self, "Подключение", "Сервер недоступен. Проверьте, запущен ли сервер.")
            self._update_status_message("Сервер недоступен", 3000)
    
    def _on_login(self):
        """Аутентификация"""
        dialog = LoginDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            username, password = dialog.get_credentials()
            if self.client.login(username, password):
                self.login_btn.setEnabled(False)
                self.logout_btn.setEnabled(True)
                self.status_label.setText(f"Авторизован: {username}")
                self._update_status_message(f"Добро пожаловать, {username}", 3000)
                self._load_modes_from_server()
            else:
                QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль")
    
    def _load_modes_from_server(self):
        """Загрузка режимов с сервера"""
        modes = self.client.get_modes()
        if modes:
            self.mode_combo.clear()
            self.mode_combo.addItems(modes)
    
    def _on_logout(self):
        """Выход из системы"""
        self.client.token = None
        self.login_btn.setEnabled(True)
        self.logout_btn.setEnabled(False)
        self.status_label.setText("Не авторизован")
        self._update_status_message("Выход выполнен", 3000)
    
    def _on_mode_changed(self, mode: str):
        """Обработчик изменения режима"""
        if self.client.token:
            if self.client.set_mode(mode):
                self._update_status_message(f"Режим изменен на {mode}", 2000)
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось изменить режим")
    
    def _update_data(self):
        """Обновление текущих данных"""
        if not self.client.token:
            return
        
        data = self.client.get_current_data()
        if data:
            reading = data.get("reading", {})
            analysis = data.get("analysis", {})
            
            # Обновление индикаторов
            self.rpm_gauge.set_value(reading.get("rpm", 0))
            self.temp_gauge.set_value(reading.get("exhaust_temp", 0))
            self.pressure_gauge.set_value(reading.get("inlet_pressure", 0))
            self.fuel_gauge.set_value(reading.get("fuel_flow", 0))
            self.vibro_gauge.set_value(reading.get("vibration", 0))
            self.iga_gauge.set_value(reading.get("iga_position", 0))
            
            # Обновление диапазонов нормы (строго по приложению 2)
            mode_name = analysis.get("mode", "STOP")
            try:
                mode_enum = Mode(mode_name)
                normals = NORMAL_RANGES.get(mode_enum, {})
            except ValueError:
                normals = {}
            
            self.rpm_gauge.set_normal_range(
                normals.get("rpm", (0, 9000))[0],
                normals.get("rpm", (0, 9000))[1]
            )
            self.temp_gauge.set_normal_range(
                normals.get("exhaust_temp", (0, 900))[0],
                normals.get("exhaust_temp", (0, 900))[1]
            )
            self.pressure_gauge.set_normal_range(
                normals.get("inlet_pressure", (95, 170))[0],
                normals.get("inlet_pressure", (95, 170))[1]
            )
            self.fuel_gauge.set_normal_range(
                normals.get("fuel_flow", (0, 3200))[0],
                normals.get("fuel_flow", (0, 3200))[1]
            )
            self.vibro_gauge.set_normal_range(
                normals.get("vibration", (0, 13))[0],
                normals.get("vibration", (0, 13))[1]
            )
            self.iga_gauge.set_normal_range(
                normals.get("iga_position", (0, 100))[0],
                normals.get("iga_position", (0, 100))[1]
            )
            
            # Обновление индикатора режима
            self.mode_indicator.set_mode(mode_name)
            self.mode_indicator.set_healthy(analysis.get("is_healthy", True))
            
            # Обновление списка аномалий
            self.anomaly_list.set_anomalies(analysis.get("anomalies", []))
            
            # Обновление статуса в статус-баре
            if not analysis.get("is_healthy", True):
                anomalies_count = len(analysis.get("anomalies", []))
                self._update_status_message(f"⚠️ Обнаружено аномалий: {anomalies_count}")
            else:
                self._update_status_message(f"✅ Режим: {mode_name} | Все параметры в норме")
    
    def _load_history(self):
        """Загрузка истории"""
        if not self.client.token:
            return
        
        mode = self.history_mode_combo.currentText()
        mode = None if mode == "Все" else mode
        
        history = self.client.get_history(100, mode)
        
        self.history_table.setRowCount(len(history))
        for i, record in enumerate(history):
            self.history_table.setItem(i, 0, QTableWidgetItem(record.get("datetime", "")))
            self.history_table.setItem(i, 1, QTableWidgetItem(str(record.get("rpm", ""))))
            self.history_table.setItem(i, 2, QTableWidgetItem(str(record.get("exhaust_temp", ""))))
            self.history_table.setItem(i, 3, QTableWidgetItem(str(record.get("inlet_pressure", ""))))
            self.history_table.setItem(i, 4, QTableWidgetItem(str(record.get("fuel_flow", ""))))
            self.history_table.setItem(i, 5, QTableWidgetItem(str(record.get("vibration", ""))))
            self.history_table.setItem(i, 6, QTableWidgetItem(str(record.get("iga_position", ""))))
            
            status = "✅ Норма" if record.get("is_healthy") else f"⚠️ Аномалий: {record.get('anomalies_count', 0)}"
            self.history_table.setItem(i, 7, QTableWidgetItem(status))
        
        self.history_table.resizeColumnsToContents()
        self._update_status_message("История обновлена", 2000)
    
    def _load_anomalies(self):
        """Загрузка журнала аномалий"""
        if not self.client.token:
            return
        
        anomalies = self.client.get_anomalies(100)
        
        self.anomalies_table.setRowCount(len(anomalies))
        for i, a in enumerate(anomalies):
            timestamp = a.get("timestamp", 0)
            if timestamp:
                time_str = datetime.fromtimestamp(timestamp).strftime("%H:%M:%S")
            else:
                time_str = ""
            
            self.anomalies_table.setItem(i, 0, QTableWidgetItem(time_str))
            self.anomalies_table.setItem(i, 1, QTableWidgetItem(a.get("mode", "")))
            self.anomalies_table.setItem(i, 2, QTableWidgetItem(a.get("parameter", "")))
            self.anomalies_table.setItem(i, 3, QTableWidgetItem(str(a.get("value", ""))))
            self.anomalies_table.setItem(i, 4, QTableWidgetItem(f"{a.get('min_normal', 0)}-{a.get('max_normal', 0)}"))
            self.anomalies_table.setItem(i, 5, QTableWidgetItem(a.get("severity", "")))
            
            if a.get("severity") == "CRITICAL":
                for col in range(6):
                    item = self.anomalies_table.item(i, col)
                    if item:
                        item.setBackground(Qt.red)
                        item.setForeground(Qt.white)
        
        self.anomalies_table.resizeColumnsToContents()
        self._update_status_message("Журнал аномалий обновлен", 2000)