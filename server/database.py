"""Модуль работы с базой данных"""

from sqlalchemy import create_engine, Column, Float, String, Boolean, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from server.config import DATABASE_URL
from datetime import datetime


Base = declarative_base()


class ReadingRecord(Base):
    """Таблица для хранения показаний"""
    __tablename__ = "readings"
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(Float, nullable=False, index=True)
    mode = Column(String(50), nullable=False)
    rpm = Column(Float, nullable=False)
    exhaust_temp = Column(Float, nullable=False)
    inlet_pressure = Column(Float, nullable=False)
    fuel_flow = Column(Float, nullable=False)
    vibration = Column(Float, nullable=False)
    iga_position = Column(Float, nullable=False)
    is_healthy = Column(Boolean, nullable=False, default=True)


class AnomalyRecordDB(Base):
    """Таблица для хранения аномалий"""
    __tablename__ = "anomalies"
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(Float, nullable=False, index=True)
    mode = Column(String(50), nullable=False)
    parameter = Column(String(50), nullable=False)
    value = Column(Float, nullable=False)
    min_normal = Column(Float, nullable=False)
    max_normal = Column(Float, nullable=False)
    severity = Column(String(20), nullable=False)


class DatabaseManager:
    """Менеджер базы данных"""
    
    def __init__(self):
        self.engine = create_engine(DATABASE_URL, echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
    
    def save_reading(self, reading, analysis_result):
        """Сохранение показания и результатов анализа"""
        session = self.Session()
        try:
            record = ReadingRecord(
                timestamp=reading.timestamp,
                mode=analysis_result.mode,
                rpm=reading.rpm,
                exhaust_temp=reading.exhaust_temp,
                inlet_pressure=reading.inlet_pressure,
                fuel_flow=reading.fuel_flow,
                vibration=reading.vibration,
                iga_position=reading.iga_position,
                is_healthy=analysis_result.is_healthy,
            )
            session.add(record)
            
            for anomaly in analysis_result.anomalies:
                anomaly_record = AnomalyRecordDB(
                    timestamp=anomaly.timestamp,
                    mode=anomaly.mode,
                    parameter=anomaly.parameter,
                    value=anomaly.value,
                    min_normal=anomaly.min_normal,
                    max_normal=anomaly.max_normal,
                    severity=anomaly.severity,
                )
                session.add(anomaly_record)
            
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_history(self, limit: int = 100) -> list:
        """Получение истории показаний"""
        session = self.Session()
        try:
            records = session.query(ReadingRecord).order_by(
                ReadingRecord.timestamp.desc()
            ).limit(limit).all()
            return records
        finally:
            session.close()
    
    def get_anomalies(self, limit: int = 100) -> list:
        """Получение истории аномалий"""
        session = self.Session()
        try:
            anomalies = session.query(AnomalyRecordDB).order_by(
                AnomalyRecordDB.timestamp.desc()
            ).limit(limit).all()
            return anomalies
        finally:
            session.close()