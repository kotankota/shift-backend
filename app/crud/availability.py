from app.models import Availability
from app.schemas.schemas import AvailabilityCreate, AvailabilityUpdate
from app.crud.base import CRUDBase

class CRUDAvailability(CRUDBase[Availability, AvailabilityCreate, AvailabilityUpdate]):
    pass

crud_availability = CRUDAvailability(Availability)
