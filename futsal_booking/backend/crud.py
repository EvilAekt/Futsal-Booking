from sqlalchemy.orm import Session
from . import models, database
from datetime import datetime, timedelta

# --- Fungsi untuk Operasi Database (CRUD) ---

def get_court(db: Session, court_id: int):
    return db.query(database.Court).filter(database.Court.id == court_id).first()

def get_courts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(database.Court).offset(skip).limit(limit).all()

def get_bookings_on_date(db: Session, court_id: int, date: str):
    return db.query(database.Booking).filter(
        database.Booking.court_id == court_id,
        database.Booking.booking_date == date
    ).all()

def create_booking(db: Session, booking: models.BookingCreate):
    court = get_court(db, booking.court_id)
    if not court:
        return None
    
    total_price = court.price * booking.duration
    
    db_booking = database.Booking(
        **booking.dict(),
        total_price=total_price,
        status="confirmed"
    )
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    return db_booking

def seed_data(db: Session):
    """Fungsi untuk mengisi data dummy jika database kosong"""
    if db.query(database.Court).first():
        return # Data sudah ada
    
    courts_data = [
            {"name": "Aneka Futsal - Indoor Premium", "type": "Indoor", "price": 120000, "facilities": "Toilet,Kantin,WiFi,Loker", "image_url": "https://i.imgur.com/HjXhLWJ.jpeg"},
            {"name": "Meteor Arena - Outdoor", "type": "Outdoor", "price": 80000, "facilities": "Toilet,Kantin,Parkir Luas", "image_url": "https://i.imgur.com/N2mf03j.jpeg"},
            {"name": "Semar Futsal Center", "type": "Indoor", "price": 100000, "facilities": "Kantin,Wifi,Toilet,Parkir", "image_url": "https://i.imgur.com/FP1qPGa.jpeg"},
            {"name": "Paragon Arena", "type": "Indoor", "price": 110000, "facilities": "Toilet,Kantin,WiFi,Parkir", "image_url": "https://i.imgur.com/O28vCzW.jpeg"},
            {"name": "Dragon Futsal - Outdoor", "type": "Outdoor", "price": 85000, "facilities": "Kantin,Toilet,Parkir", "image_url": "https://i.imgur.com/ZZt0CUa.jpeg"},
            {"name": "Milwal Sports Center - Premium", "type": "Premium", "price": 150000, "facilities": "AC,Toilet,Kantin,WiFi,Loker,Shower", "image_url": "https://i.imgur.com/QQl6WVM.jpeg"},
            {"name": "Sintesis Arena", "type": "Indoor", "price": 95000, "facilities": "Toilet,Kantin,Wifi,Parkir Luas", "image_url": "https://i.imgur.com/3jlvTn1.jpeg"},
        ]
    
    for court_data in courts_data:
        db_court = database.Court(**court_data)
        db.add(db_court)
    
    db.commit()
    print("Dummy data has been seeded.")
    
    