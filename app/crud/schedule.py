from app.models import Schedule
from app.schemas.schemas import ScheduleCreate, ScheduleUpdate
from app.crud.base import CRUDBase
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date

class CRUDSchedule(CRUDBase[Schedule, ScheduleCreate, ScheduleUpdate]):
    def remove_all(self, db: Session) -> None:
        db.query(Schedule).delete()
        db.commit()

crud_schedule = CRUDSchedule(Schedule)
