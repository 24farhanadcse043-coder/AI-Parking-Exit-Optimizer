from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import ParkingSpace, Vehicle, ParkingExit


router = APIRouter(
    prefix="/api/dashboard",
    tags=["Dashboard"]
)


# ---------------------------------------------------------
# Create dashboard data
# ---------------------------------------------------------

def get_dashboard_data(db: Session):

    # -----------------------------------------------------
    # Parking information
    # -----------------------------------------------------

    spaces = db.query(
        ParkingSpace
    ).all()

    total_spaces = len(spaces)

    occupied_spaces = sum(
        1
        for space in spaces
        if space.occupied
    )

    available_spaces = (
        total_spaces - occupied_spaces
    )

    occupancy_percentage = (
        (occupied_spaces / total_spaces) * 100
        if total_spaces > 0
        else 0
    )

    # -----------------------------------------------------
    # Vehicle information
    # -----------------------------------------------------

    parked_vehicles = (
        db.query(Vehicle)
        .filter(
            Vehicle.status == "PARKED"
        )
        .all()
    )

    entered_vehicles = (
        db.query(Vehicle)
        .filter(
            Vehicle.status == "ENTERED"
        )
        .all()
    )

    exited_vehicles = (
        db.query(Vehicle)
        .filter(
            Vehicle.status == "EXITED"
        )
        .all()
    )

    # -----------------------------------------------------
    # Vehicle details
    # -----------------------------------------------------

    vehicle_data = []

    for vehicle in parked_vehicles:

        vehicle_data.append({

            "id":
                vehicle.id,

            "vehicle_number":
                vehicle.vehicle_number,

            "parking_space":
                vehicle.parking_space,

            "current_location":
                vehicle.current_location,

            "status":
                vehicle.status
        })

    # -----------------------------------------------------
    # Exit information
    # -----------------------------------------------------

    exits = db.query(
        ParkingExit
    ).all()

    exit_data = []

    for parking_exit in exits:

        exit_data.append({

            "id":
                parking_exit.id,

            "name":
                parking_exit.name,

            "queue_length":
                parking_exit.queue_length,

            "waiting_time":
                parking_exit.waiting_time,

            "distance":
                parking_exit.distance,

            "congestion_level":
                parking_exit.congestion_level,

            "is_available":
                parking_exit.is_available
        })

    # -----------------------------------------------------
    # Dashboard response
    # -----------------------------------------------------

    return {

        "parking": {

            "total_spaces":
                total_spaces,

            "occupied_spaces":
                occupied_spaces,

            "available_spaces":
                available_spaces,

            "occupancy_percentage":
                round(
                    occupancy_percentage,
                    2
                )
        },

        "vehicles": {

            "parked":
                len(parked_vehicles),

            "entered":
                len(entered_vehicles),

            "exited":
                len(exited_vehicles),

            "total_registered":
                db.query(Vehicle).count(),

            "parked_vehicle_details":
                vehicle_data
        },

        "exits":
            exit_data
    }


# ---------------------------------------------------------
# Dashboard REST API
# ---------------------------------------------------------

@router.get("/overview")
def dashboard_overview(
    db: Session = Depends(get_db)
):

    return get_dashboard_data(db)