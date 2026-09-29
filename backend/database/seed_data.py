import os
import sys

# Add the backend folder to Python's import path
backend_path = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

sys.path.insert(0, backend_path)

from database import SessionLocal
from models import ParkingSpace, ParkingExit


def create_parking_spaces(db):
    existing_count = db.query(ParkingSpace).count()

    if existing_count > 0:
        print("Parking spaces already exist.")
        return

    for i in range(1, 101):
        space = ParkingSpace(
            space_number=f"P{i:03d}",
            occupied=False
        )

        db.add(space)

    db.commit()

    print("100 parking spaces created.")


def create_exits(db):
    existing_count = db.query(ParkingExit).count()

    if existing_count > 0:
        print("Parking exits already exist.")
        return

    exits = [
        ParkingExit(
            name="Exit A",
            queue_length=14,
            waiting_time=8,
            distance=120,
            congestion_level="HIGH",
            is_available=True
        ),

        ParkingExit(
            name="Exit B",
            queue_length=4,
            waiting_time=2,
            distance=180,
            congestion_level="LOW",
            is_available=True
        ),

        ParkingExit(
            name="Exit C",
            queue_length=8,
            waiting_time=5,
            distance=150,
            congestion_level="MEDIUM",
            is_available=True
        )
    ]

    db.add_all(exits)
    db.commit()

    print("3 parking exits created.")


def main():
    db = SessionLocal()

    try:
        create_parking_spaces(db)
        create_exits(db)

    finally:
        db.close()

    print("Database setup completed.")


if __name__ == "__main__":
    main()