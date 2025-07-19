from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Dict
from datetime import datetime, timedelta

from . import crud, models, database

# Buat tabel di database
database.create_db_and_tables()

app = FastAPI()

# Atur CORS agar frontend bisa mengakses API
origins = [
    "http://localhost",
    "http://localhost:8501", # Port default Streamlit
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency untuk mendapatkan session DB
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
def on_startup():
    # Isi database dengan data dummy saat aplikasi pertama kali dijalankan
    db = database.SessionLocal()
    crud.seed_data(db)
    db.close()

# --- API Endpoints ---

@app.get("/courts/", response_model=List[models.Court])
def read_courts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    courts = crud.get_courts(db, skip=skip, limit=limit)
    return courts

@app.get("/courts/{court_id}/availability")
def get_availability(court_id: int, date: str, db: Session = Depends(get_db)):
    court = crud.get_court(db, court_id)
    if not court:
        raise HTTPException(status_code=404, detail="Court not found")

    bookings = crud.get_bookings_on_date(db, court_id, date)
    booked_slots = set()
    for b in bookings:
        start_hour = int(b.start_time.split(':')[0])
        for i in range(b.duration):
            booked_slots.add(f"{start_hour + i:02d}:00")

    start_op, end_op = court.operating_hours.split('-')
    start_hour_op = int(start_op.split(':')[0])
    end_hour_op = int(end_op.split(':')[0])

    available_slots = []
    for hour in range(start_hour_op, end_hour_op):
        time_slot = f"{hour:02d}:00"
        if time_slot not in booked_slots:
            available_slots.append(time_slot)
            
    return {"available_slots": available_slots}


@app.post("/bookings/", response_model=models.Booking)
def create_booking(booking: models.BookingCreate, db: Session = Depends(get_db)):
    # Cek ketersediaan sekali lagi sebelum membuat booking
    bookings = crud.get_bookings_on_date(db, booking.court_id, booking.booking_date)
    start_hour = int(booking.start_time.split(':')[0])
    
    for i in range(booking.duration):
        check_time = f"{start_hour + i:02d}:00"
        for b in bookings:
            booked_start_hour = int(b.start_time.split(':')[0])
            if check_time in [f"{booked_start_hour+j:02d}:00" for j in range(b.duration)]:
                raise HTTPException(status_code=409, detail=f"Slot at {check_time} is already booked.")

    return crud.create_booking(db=db, booking=booking)


