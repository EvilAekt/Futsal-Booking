from pydantic import BaseModel
from typing import List

# --- Skema Pydantic untuk API ---

class BookingBase(BaseModel):
    court_id: int
    customer_name: str
    customer_phone: str
    customer_email: str
    booking_date: str
    start_time: str
    duration: int

class BookingCreate(BookingBase):
    pass

class Booking(BookingBase):
    id: int
    total_price: float
    status: str

    class Config:
        orm_mode = True

class CourtBase(BaseModel):
    name: str
    type: str
    price: float
    facilities: str
    image_url: str
    operating_hours: str

class Court(CourtBase):
    id: int
    bookings: List[Booking] = []

    class Config:
        orm_mode = True