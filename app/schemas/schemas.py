from pydantic import BaseModel, EmailStr, ConfigDict
from pydantic.alias_generators import to_camel
from typing import List, Optional
from datetime import datetime, date


class BaseSchema(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel
    )   


class UserBase(BaseSchema):
    name: str
    email: EmailStr
    role: Optional[str] = "employee"

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseSchema):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[str] = None

class User(UserBase):
    id: str

    class Config:
        orm_mode = True

class AvailabilityBase(BaseSchema):
    date: date
    is_available: bool

class AvailabilityCreate(AvailabilityBase):
    pass

class AvailabilityUpdate(BaseSchema):
    is_available: Optional[bool] = None

class Availability(AvailabilityBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class ScheduleBase(BaseSchema):
    date: date
    assigned: bool

class ScheduleCreate(ScheduleBase):
    user_id: str

class ScheduleUpdate(BaseSchema):
    assigned: Optional[bool] = None

class Schedule(ScheduleBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class DailyConstraintBase(BaseSchema):
    date: date
    min_employees: int
    max_employees: int
    is_holiday: Optional[bool] = False

class DailyConstraintCreate(DailyConstraintBase):
    pass

class DailyConstraintUpdate(BaseSchema):
    min_employees: Optional[int] = None
    max_employees: Optional[int] = None
    is_holiday: Optional[bool] = None

class DailyConstraint(DailyConstraintBase):
    id: str
    date_updated: datetime

    class Config:
        orm_mode = True

class Token(BaseSchema):
    access_token: str
    token_type: str
    user_id: str
    role: str
    name: str
    
class TokenData(BaseSchema):
    email: Optional[str] = None


class Login(BaseSchema):
    username: str
    password: str

class WeekdayDefaults(BaseSchema):
    weekday: int
    min_employees: int
    max_employees: int

class HolidayDefaults(BaseSchema):
    min_employees: int
    max_employees: int