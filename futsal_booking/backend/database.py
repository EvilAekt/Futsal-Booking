import os
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from datetime import datetime

# Path untuk file database SQLite
DATABASE_URL = "sqlite:///./futsal.db"

# Hapus file DB lama jika ada, untuk memulai dari awal setiap kali dijalankan (opsional)
if os.path.exists("./futsal.db"):
    os.remove("./futsal.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- Model Tabel Database ---
class Court(Base):
    __tablename__ = "courts"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    type = Column(String) # Indoor, Outdoor, Premium
    price = Column(Float)
    facilities = Column(String) # "AC,Toilet,Kantin"
    image_url = Column(String)
    operating_hours = Column(String, default="08:00-22:00") # Format "HH:MM-HH:MM"

    bookings = relationship("Booking", back_populates="court")

class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    court_id = Column(Integer, ForeignKey("courts.id"))
    customer_name = Column(String)
    customer_phone = Column(String)
    customer_email = Column(String)
    booking_date = Column(String) # "YYYY-MM-DD"
    start_time = Column(String) # "HH:MM"
    duration = Column(Integer) # in hours
    total_price = Column(Float)
    status = Column(String, default="confirmed")
    created_at = Column(DateTime, default=datetime.utcnow)

    court = relationship("Court", back_populates="bookings")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_db_and_tables():
    Base.metadata.create_all(bind=engine)