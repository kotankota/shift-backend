from app.models import DailyConstraint
from app.schemas.schemas import DailyConstraintCreate, DailyConstraintUpdate
from app.crud.base import CRUDBase
from typing import Optional
from sqlalchemy.orm import Session
from datetime import date

class CRUDDailyConstraint(CRUDBase[DailyConstraint, DailyConstraintCreate, DailyConstraintUpdate]):
    def get_by_date(self, db: Session, *, date: date) -> Optional[DailyConstraint]:
        return db.query(DailyConstraint).filter(DailyConstraint.date == date).first()

crud_daily_constraint = CRUDDailyConstraint(DailyConstraint)
