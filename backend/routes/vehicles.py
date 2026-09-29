from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Vehicle, ParkingSpace

from utils.websocket_manager import manager
from utils.dashboard_manager import dashboard_manager


router = APIRouter(
    prefix="/api/vehicles",
    tags=["Vehicles"]
)


# ---------------------------------------------------------
# Get all vehicles
# ---------------------------------------------------------

@router.get("/")
def get_vehicles(
    db: Session = Depends(get_db)
):
    vehicles = db.query(Vehicle).all()

    return [
        {
            "id": vehicle.id,
            "vehicle_number": vehicle.vehicle_number,
            "entry_time": vehicle.entry_time,
            "parking_space": vehicle.parking_space,
            "current_location": vehicle.current_location,
            "status": vehicle.status
        }
        for vehicle in vehicles
    ]


# ---------------------------------------------------------
# Get current parking occupancy
# ---------------------------------------------------------

def get_occupancy_data(db):

    spaces = db.query(ParkingSpace).all()

    total_spaces = len(spaces)

    occupied_spaces = sum(
        1
        for space in spaces
        if space.occupied
    )

    available_spaces = (
        total_spaces -
        occupied_spaces
    )

    occupancy_percentage = (
        (occupied_spaces / total_spaces) * 100
        if total_spaces > 0
        else 0
    )

    return {
        "total_spaces": total_spaces,
        "occupied_spaces": occupied_spaces,
        "available_spaces": available_spaces,
        "occupancy_percentage": round(
            occupancy_percentage,
            2
        )
    }


# ---------------------------------------------------------
# Broadcast parking occupancy through WebSocket
# ---------------------------------------------------------

async def broadcast_occupancy(db):

    occupancy_data = get_occupancy_data(db)

    message = {
        "type": "PARKING_UPDATE",
        "data": occupancy_data
    }

    await manager.broadcast(message)

    from routes.dashboard import get_dashboard_data

    dashboard_data = get_dashboard_data(db)

    dashboard_message = {
        "type": "DASHBOARD_UPDATE",
        "data": dashboard_data
    }

    await dashboard_manager.broadcast(
        dashboard_message
    )


# ---------------------------------------------------------
# Vehicle Entry
# ---------------------------------------------------------

@router.post("/entry")
def vehicle_entry(
    vehicle_number: str,
    db: Session = Depends(get_db)
):

    existing_vehicle = (
        db.query(Vehicle)
        .filter(
            Vehicle.vehicle_number == vehicle_number
        )
        .first()
    )

    if existing_vehicle:

        raise HTTPException(
            status_code=400,
            detail=(
                "Vehicle is already inside "
                "the parking system"
            )
        )

    vehicle = Vehicle(
        vehicle_number=vehicle_number,
        status="ENTERED"
    )

    db.add(vehicle)

    db.commit()

    db.refresh(vehicle)

    return {
        "message": "Vehicle entry recorded",
        "vehicle_id": vehicle.id,
        "vehicle_number": vehicle.vehicle_number,
        "status": vehicle.status
    }


# ---------------------------------------------------------
# Park Vehicle
# ---------------------------------------------------------

@router.post("/park")
async def park_vehicle(
    vehicle_number: str,
    space_number: str,
    current_location: str = "Zone A",
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

    # Find parking space

    space = (
        db.query(ParkingSpace)
        .filter(
            ParkingSpace.space_number == space_number
        )
        .first()
    )

    if not space:

        raise HTTPException(
            status_code=404,
            detail="Parking space not found"
        )

    # Check whether space is occupied

    if space.occupied:

        raise HTTPException(
            status_code=400,
            detail="Parking space is already occupied"
        )

    # Update parking space

    space.occupied = True

    space.vehicle_number = vehicle_number

    # Update vehicle

    vehicle.parking_space = space_number

    vehicle.current_location = current_location

    vehicle.status = "PARKED"

    db.commit()

    # Broadcast occupancy

    await broadcast_occupancy(db)

    return {
        "message": "Vehicle parked successfully",
        "vehicle_number": vehicle_number,
        "parking_space": space_number,
        "current_location": current_location,
        "status": "PARKED"
    }


# ---------------------------------------------------------
# Vehicle Exit
# ---------------------------------------------------------

@router.post("/exit")
async def vehicle_exit(
    vehicle_number: str,
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

    # Free parking space

    if vehicle.parking_space:

        space = (
            db.query(ParkingSpace)
            .filter(
                ParkingSpace.space_number
                == vehicle.parking_space
            )
            .first()
        )

        if space:

            space.occupied = False

            space.vehicle_number = None

    # Update vehicle status

    vehicle.status = "EXITED"

    vehicle.parking_space = None

    vehicle.current_location = None

    db.commit()

    # Broadcast occupancy

    await broadcast_occupancy(db)

    return {
        "message": "Vehicle exit recorded",
        "vehicle_number": vehicle_number,
        "status": "EXITED"
    }