from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Vehicle

from routes.route_guidance import calculate_vehicle_route
from routes.route_guidance import broadcast_vehicle_route


router = APIRouter(
    prefix="/api/simulation",
    tags=["Vehicle Simulation"]
)


# ---------------------------------------------------------
# Move vehicle to another zone
# ---------------------------------------------------------

@router.put("/move/{vehicle_number}")
async def move_vehicle(
    vehicle_number: str,
    location: str,
    db: Session = Depends(get_db)
):

    # Find vehicle
    vehicle = (
        db.query(Vehicle)
        .filter(
            Vehicle.vehicle_number == vehicle_number
        )
        .first()
    )

    if not vehicle:

        raise HTTPException(
            status_code=404,
            detail="Vehicle not found"
        )

    # Vehicle must be parked
    if vehicle.status != "PARKED":

        raise HTTPException(
            status_code=400,
            detail="Vehicle must be PARKED before movement"
        )

    # Validate location
    allowed_locations = [
        "Zone A",
        "Zone B",
        "Zone C"
    ]

    if location not in allowed_locations:

        raise HTTPException(
            status_code=400,
            detail="Invalid location. Use Zone A, Zone B, or Zone C."
        )

    # Update vehicle location
    vehicle.current_location = location

    db.commit()
    db.refresh(vehicle)

    # Calculate new route
    route = calculate_vehicle_route(
        vehicle_number,
        db
    )

    # Send route update
    await broadcast_vehicle_route(
        vehicle_number,
        db
    )

    return {
        "message": "Vehicle moved successfully",
        "vehicle_number": vehicle.vehicle_number,
        "current_location": vehicle.current_location,
        "status": vehicle.status,
        "new_route": route
    }


# ---------------------------------------------------------
# Get vehicle simulation status
# ---------------------------------------------------------

@router.get("/status/{vehicle_number}")
def simulation_status(
    vehicle_number: str,
    db: Session = Depends(get_db)
):

    vehicle = (
        db.query(Vehicle)
        .filter(
            Vehicle.vehicle_number == vehicle_number
        )
        .first()
    )

    if not vehicle:

        raise HTTPException(
            status_code=404,
            detail="Vehicle not found"
        )

    route = calculate_vehicle_route(
        vehicle_number,
        db
    )

    return {
        "vehicle_number": vehicle.vehicle_number,
        "status": vehicle.status,
        "current_location": vehicle.current_location,
        "parking_space": vehicle.parking_space,
        "route": route
    }