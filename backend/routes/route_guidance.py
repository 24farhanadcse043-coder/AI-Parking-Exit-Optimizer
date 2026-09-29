from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Vehicle, ParkingExit

from ai.route_optimizer import find_best_exit
from utils.route_manager import route_manager


router = APIRouter(
    prefix="/api/routes",
    tags=["Route Guidance"]
)


# ---------------------------------------------------------
# Route distances from each parking zone to each exit
# ---------------------------------------------------------

ROUTE_DISTANCES = {

    "Zone A": {
        "Exit A": 100,
        "Exit B": 180,
        "Exit C": 150
    },

    "Zone B": {
        "Exit A": 160,
        "Exit B": 120,
        "Exit C": 200
    },

    "Zone C": {
        "Exit A": 220,
        "Exit B": 140,
        "Exit C": 100
    }
}


# ---------------------------------------------------------
# Calculate route for a vehicle
# ---------------------------------------------------------

def calculate_vehicle_route(
    vehicle_number,
    db
):

    vehicle = (
        db.query(Vehicle)
        .filter(
            Vehicle.vehicle_number == vehicle_number
        )
        .first()
    )

    if not vehicle:
        return None

    if not vehicle.current_location:
        return None

    if vehicle.current_location not in ROUTE_DISTANCES:
        return None

    # Get available exits
    exits = (
        db.query(ParkingExit)
        .filter(
            ParkingExit.is_available == True
        )
        .all()
    )

    if not exits:
        return None

    route_data = []

    # ---------------------------------------------
    # Build route information
    # ---------------------------------------------

    for parking_exit in exits:

        exit_distance = ROUTE_DISTANCES[
            vehicle.current_location
        ].get(
            parking_exit.name
        )

        if exit_distance is None:
            continue

        route_data.append({

            "name": parking_exit.name,

            "queue_length":
                parking_exit.queue_length,

            "waiting_time":
                parking_exit.waiting_time,

            "distance":
                exit_distance,

            "congestion_level":
                parking_exit.congestion_level,

            "is_available":
                parking_exit.is_available
        })

    if not route_data:
        return None

    # ---------------------------------------------
    # AI chooses best exit
    # ---------------------------------------------

    recommendation = find_best_exit(
        route_data
    )

    if recommendation is None:
        return None

    recommended = (
        recommendation["recommended_exit"]
    )

    # ---------------------------------------------
    # Build route response
    # ---------------------------------------------

    return {

        "status": "SUCCESS",

        "vehicle_number":
            vehicle.vehicle_number,

        "current_location":
            vehicle.current_location,

        "recommended_exit":
            recommended["name"],

        "distance":
            recommended["distance"],

        "estimated_waiting_time":
            recommended["waiting_time"],

        "congestion":
            recommended["congestion_level"],

        "ai_score":
            recommended["score"],

        "route": [
            vehicle.current_location,
            "Parking Exit",
            recommended["name"]
        ],

        "alternative_routes":
            recommendation["alternative_exits"]
    }


# ---------------------------------------------------------
# Get current route for a vehicle
# ---------------------------------------------------------

@router.get("/{vehicle_number}")
def get_vehicle_route(
    vehicle_number: str,
    db: Session = Depends(get_db)
):

    route = calculate_vehicle_route(
        vehicle_number,
        db
    )

    if route is None:

        raise HTTPException(
            status_code=404,
            detail="Unable to calculate vehicle route"
        )

    return route


# ---------------------------------------------------------
# Send updated route to vehicle
# ---------------------------------------------------------

async def broadcast_vehicle_route(
    vehicle_number: str,
    db: Session
):

    route = calculate_vehicle_route(
        vehicle_number,
        db
    )

    if route is None:
        return

    message = {

        "type":
            "VEHICLE_ROUTE_UPDATE",

        "data":
            route
    }

    await route_manager.send_to_vehicle(
        vehicle_number,
        message
    )