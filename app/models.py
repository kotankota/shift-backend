from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Date
from sqlalchemy.orm import relationship
from .database import Base
import uuid
import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="employee")
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc)) 
    updated_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc), onupdate=datetime.datetime.now(datetime.timezone.utc)) 
        
    availabilities = relationship("Availability", back_populates="user")
    schedules = relationship("Schedule", back_populates="user")

class Availability(Base):
    __tablename__ = "availabilities"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"))
    date = Column(Date, nullable=False)
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc)) 
    updated_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc), onupdate=datetime.datetime.now(datetime.timezone.utc)) 

    user = relationship("User", back_populates="availabilities")

class Schedule(Base):
    __tablename__ = "schedules"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    date = Column(Date, nullable=False)
    user_id = Column(String, ForeignKey("users.id"))
    assigned = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc)) 
    updated_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc), onupdate=datetime.datetime.now(datetime.timezone.utc)) 

    user = relationship("User", back_populates="schedules")

class DailyConstraint(Base):
    __tablename__ = "daily_constraints"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    date = Column(Date, nullable=False, unique=True)
    min_employees = Column(Integer, nullable=False)
    max_employees = Column(Integer, nullable=False)
    is_holiday = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc)) 
    updated_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc), onupdate=datetime.datetime.now(datetime.timezone.utc)) 

    def __init__(self, date, min_employees=None, max_employees=None, is_holiday=False):
        self.date = date
        self.is_holiday = is_holiday
        self.date_updated = datetime.datetime.utcnow()

        # 曜日ごとのデフォルト値を設定
        weekday = date.weekday()
        defaults = DefaultSettings.get_default_settings(weekday, is_holiday)
        self.min_employees = min_employees if min_employees is not None else defaults.min_employees
        self.max_employees = max_employees if max_employees is not None else defaults.max_employees

class DefaultSettings(Base):
    __tablename__ = "default_settings"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    weekday = Column(Integer, nullable=False)
    min_employees = Column(Integer, nullable=False)
    max_employees = Column(Integer, nullable=False)
    is_holiday = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc)) 
    updated_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc), onupdate=datetime.datetime.now(datetime.timezone.utc)) 

    @staticmethod
    def get_default_settings(db, weekday, is_holiday):
        return db.query(DefaultSettings).filter_by(weekday=weekday, is_holiday=is_holiday).first()

    @staticmethod
    def set_default_settings(db, weekday, min_employees, max_employees, is_holiday):
        default_setting = db.query(DefaultSettings).filter_by(weekday=weekday, is_holiday=is_holiday).first()
        if default_setting:
            default_setting.min_employees = min_employees
            default_setting.max_employees = max_employees
        else:
            default_setting = DefaultSettings(
                weekday=weekday,
                min_employees=min_employees,
                max_employees=max_employees,
                is_holiday=is_holiday
            )
            db.add(default_setting)
        db.commit()
        return default_setting
