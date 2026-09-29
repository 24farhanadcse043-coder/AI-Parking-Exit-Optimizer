from database import SessionLocal
from models import ParkingSpace


def update_parking_database(parking_status):

    db = SessionLocal()

    try:

        updated_count = 0

        for status in parking_status:

            space = (
                db.query(ParkingSpace)
                .filter(
                    ParkingSpace.space_number
                    == status["space_number"]
                )
                .first()
            )

            if not space:
                continue

            space.occupied = status["occupied"]

            vehicle = status.get("vehicle")

            if vehicle:

                vehicle_type = vehicle.get(
                    "type",
                    "vehicle"
                )

                space.vehicle_number = (
                    f"VISION_{vehicle_type}"
                )

            else:

                space.vehicle_number = None

            updated_count += 1

        db.commit()

        return {
            "status": "SUCCESS",
            "updated_spaces": updated_count
        }

    except Exception as error:

        db.rollback()

        print(
            f"❌ Database update error: {error}"
        )

        return {
            "status": "ERROR",
            "message": str(error)
        }

    finally:

        db.close()