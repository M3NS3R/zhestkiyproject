"""Виджеты для PyQt5 интерфейса"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QProgressBar, QFrame, QGroupBox, QGridLayout
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor


class GaugeWidget(QWidget):
    """Виджет-индикатор (аналог шкалы прибора)"""
    
    def __init__(self, title: str, unit: str, min_val: float, max_val: float, parent=None):
        super().__init__(parent)
        self.title = title
        self.unit = unit
        self.min_val = min_val
        self.max_val = max_val
        self.current_value = 0.0
        self.normal_min = min_val
        self.normal_max = max_val
        
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout()
        
        # Заголовок
        self.title_label = QLabel(self.title)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setFont(QFont("Arial", 10, QFont.Bold))
        layout.addWidget(self.title_label)
        
        # Значение
        self.value_label = QLabel("0.00")
        self.value_label.setAlignment(Qt.AlignCenter)
        self.value_label.setFont(QFont("Arial", 18, QFont.Bold))
        layout.addWidget(self.value_label)
        
        # Единица измерения
        self.unit_label = QLabel(self.unit)
        self.unit_label.setAlignment(Qt.AlignCenter)
        self.unit_label.setFont(QFont("Arial", 9))
        layout.addWidget(self.unit_label)
        
        # Прогресс бар
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setTextVisible(False)
        layout.addWidget(self.progress)
        
        # Норма
        self.norm_label = QLabel(f"Норма: {self.normal_min} - {self.normal_max} {self.unit}")
        self.norm_label.setAlignment(Qt.AlignCenter)
        self.norm_label.setFont(QFont("Arial", 8))
        layout.addWidget(self.norm_label)
        
        self.setLayout(layout)
        self.setFixedHeight(120)
        self.setFixedWidth(160)
    
    def set_normal_range(self, min_val: float, max_val: float):
        """Установка диапазона нормы"""
        self.normal_min = min_val
        self.normal_max = max_val
        self.norm_label.setText(f"Норма: {min_val:.1f} - {max_val:.1f} {self.unit}")
        self.update_style()
    
    def set_value(self, value: float):
        """Установка значения"""
        self.current_value = value
        self.value_label.setText(f"{value:.2f}")
        
        # Рассчет процента для прогресс-бара
        percent = (value - self.min_val) / (self.max_val - self.min_val) * 100
        percent = max(0, min(100, percent))
        self.progress.setValue(int(percent))
        
        self.update_style()
    
    def update_style(self):
        """Обновление стиля в зависимости от нормы"""
        is_normal = self.normal_min <= self.current_value <= self.normal_max
        
        if is_normal:
            self.value_label.setStyleSheet("color: green;")
            self.progress.setStyleSheet("""
                QProgressBar::chunk { background-color: green; }
            """)
        else:
            self.value_label.setStyleSheet("color: red;")
            self.progress.setStyleSheet("""
                QProgressBar::chunk { background-color: red; }
            """)


class ModeIndicator(QWidget):
    """Индикатор текущего режима"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout()
        
        self.label = QLabel("Текущий режим:")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFont(QFont("Arial", 12))
        
        self.mode_label = QLabel("STOP")
        self.mode_label.setAlignment(Qt.AlignCenter)
        self.mode_label.setFont(QFont("Arial", 20, QFont.Bold))
        
        layout.addWidget(self.label)
        layout.addWidget(self.mode_label)
        self.setLayout(layout)
    
    def set_mode(self, mode: str):
        """Установка режима с цветовой индикацией"""
        self.mode_label.setText(mode)
        
        colors = {
            "STOP": "gray",
            "START": "orange",
            "IDLE": "blue",
            "PARTIAL": "green",
            "NOMINAL": "darkgreen",
            "EMERGENCY": "red",
        }
        color = colors.get(mode, "black")
        self.mode_label.setStyleSheet(f"color: {color};")
    
    def set_healthy(self, is_healthy: bool):
        """Индикация состояния здоровья"""
        if is_healthy:
            self.label.setText("✅ Состояние: НОРМА")
            self.label.setStyleSheet("color: green;")
        else:
            self.label.setText("⚠️ Состояние: АНОМАЛИЯ")
            self.label.setStyleSheet("color: red;")


class AnomalyListWidget(QGroupBox):
    """Виджет списка аномалий"""
    
    def __init__(self, parent=None):
        super().__init__("Аномалии", parent)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout()
        self.text_area = QLabel("Нет аномалий")
        self.text_area.setWordWrap(True)
        self.text_area.setAlignment(Qt.AlignTop)
        self.text_area.setStyleSheet("background-color: #f0f0f0; padding: 5px;")
        self.text_area.setMinimumHeight(150)
        
        layout.addWidget(self.text_area)
        self.setLayout(layout)
    
    def set_anomalies(self, anomalies: list):
        """Отображение списка аномалий"""
        if not anomalies:
            self.text_area.setText("Нет аномалий")
            self.text_area.setStyleSheet("background-color: #f0f0f0; padding: 5px; color: black;")
            return
        
        text = ""
        for a in anomalies:
            severity_icon = "🔴" if a.get("severity") == "CRITICAL" else "🟡"
            text += f"{severity_icon} {a.get('parameter')}: {a.get('value')} "
            text += f"(норма: {a.get('min_normal')} - {a.get('max_normal')})\n"
        
        self.text_area.setText(text)
        self.text_area.setStyleSheet("background-color: #ffe0e0; padding: 5px; color: red;")