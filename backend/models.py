from sqlalchemy import Column, Integer, String, Float, Boolean
from database import Base


class ParkingSpace(Base):
    __tablename__ = "parking_spaces"

    id = Column(Integer, primary_key=True, index=True)

    space_number = Column(
        String(20),
        unique=True,
        nullable=False
    )

    occupied = Column(
        Boolean,
        default=False
    )

    vehicle_number = Column(
        String(50),
        nullable=True
    )


class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)

    vehicle_number = Column(
        String(50),
        unique=True,
        nullable=False
    )

    entry_time = Column(
        String(50),
        nullable=True
    )

    parking_space = Column(
        String(20),
        nullable=True
    )

    current_location = Column(
        String(100),
        nullable=True
    )

    status = Column(
        String(30),
        default="PARKED"
    )


class ParkingExit(Base):
    __tablename__ = "parking_exits"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(
        String(50),
        unique=True,
        nullable=False
    )

    queue_length = Column(
        Integer,
        default=0
    )

    waiting_time = Column(
        Float,
        default=0.0
    )

    distance = Column(
        Float,
        default=0.0
    )

    congestion_level = Column(
        String(20),
        default="LOW"
    )

    is_available = Column(
        Boolean,
        default=True
    )