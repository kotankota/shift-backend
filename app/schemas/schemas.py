from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime, date

class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: Optional[str] = "employee"

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[str] = None

class User(UserBase):
    id: str

    class Config:
        orm_mode = True

class AvailabilityBase(BaseModel):
    date: date
    isAvailable: bool

class AvailabilityCreate(AvailabilityBase):
    pass

class AvailabilityUpdate(BaseModel):
    isAvailable: Optional[bool] = None

class Availability(AvailabilityBase):
    id: str
    userId: str
    timestamp: datetime

    class Config:
        orm_mode = True

class ScheduleBase(BaseModel):
    date: date
    assigned: bool

class ScheduleCreate(ScheduleBase):
    userId: str

class ScheduleUpdate(BaseModel):
    assigned: Optional[bool] = None

class Schedule(ScheduleBase):
    id: str
    userId: str
    timestamp: datetime

    class Config:
        orm_mode = True

class DailyConstraintBase(BaseModel):
    date: date
    minEmployees: int
    maxEmployees: int
    isHoliday: Optional[bool] = False

class DailyConstraintCreate(DailyConstraintBase):
    pass

class DailyConstraintUpdate(BaseModel):
    minEmployees: Optional[int] = None
    maxEmployees: Optional[int] = None
    isHoliday: Optional[bool] = None

class DailyConstraint(DailyConstraintBase):
    id: str
    dateUpdated: datetime

    class Config:
        orm_mode = True

class Token(BaseModel):
    accessToken: str
    tokenType: str
    userId: str
    role: str

class TokenData(BaseModel):
    email: Optional[str] = None


class Login(BaseModel):
    username: str
    password: str

class WeekdayDefaults(BaseModel):
    weekday: int
    minEmployees: int
    maxEmployees: int

class HolidayDefaults(BaseModel):
    minEmployees: int
    maxEmployees: int