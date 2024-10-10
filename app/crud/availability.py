from app.models import Availability, User
from app.schemas.schemas import AvailabilityCreate, AvailabilityUpdate
from app.crud.base import CRUDBase
from sqlalchemy.orm import Session
from typing import List
from datetime import date, timedelta

class CRUDAvailability(CRUDBase[Availability, AvailabilityCreate, AvailabilityUpdate]):
    def get_by_user_id(self, db: Session, user_id: str) -> List[Availability]:
        return db.query(Availability).filter(Availability.user_id == user_id).all()

    # TODO: レスポンスの返し方、DB構造と違う形のデータを返す時の方法
    def get_monthly(self, db: Session, month: int, year: int) -> List[dict]:
        start_date = date(year, month, 1)
        end_date = (start_date + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        result = []
        users = db.query(User).filter(User.role == "employee").all()
        for user in users:
            user_data = {
                "name": user.name,
                "availabilities": []
            }
            availabilities = self.get_by_user_id(db, user.id)
            for availability in availabilities:
                if start_date <= availability.date <= end_date:
                    user_data["availabilities"].append(availability)
            result.append(user_data)
        
        return result

crud_availability = CRUDAvailability(Availability)
