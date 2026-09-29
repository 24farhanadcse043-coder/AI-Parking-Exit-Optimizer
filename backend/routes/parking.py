from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import ParkingSpace
from utils.websocket_manager import manager

router = APIRouter(
    prefix="/api/parking",
    tags=["Parking"]
)


def get_occupancy_data(db):
    spaces = db.query(ParkingSpace).all()

    total_spaces = len(spaces)

    occupied_spaces = sum(
        1 for space in spaces
        if space.occupied
    )

    available_spaces = total_spaces - occupied_spaces

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


@router.get("/status")
def parking_status(
    db: Session = Depends(get_db)
):
    return get_occupancy_data(db)


@router.get("/spaces")
def get_parking_spaces(
    db: Session = Depends(get_db)
):
    spaces = db.query(ParkingSpace).all()

    return [
        {
            "id": space.id,
            "space_number": space.space_number,
            "occupied": space.occupied,
            "vehicle_number": space.vehicle_number
        }
        for space in spaces
    ]


@router.get("/occupied")
def get_occupied_spaces(
    db: Session = Depends(get_db)
):
    spaces = (
        db.query(ParkingSpace)
        .filter(ParkingSpace.occupied == True)
        .all()
    )

    return [
        {
            "space_number": space.space_number,
            "vehicle_number": space.vehicle_number
        }
        for space in spaces
    ]


@router.get("/available")
def get_available_spaces(
    db: Session = Depends(get_db)
):
    spaces = (
        db.query(ParkingSpace)
        .filter(ParkingSpace.occupied == False)
        .all()
    )

    return [
        {
            "space_number": space.space_number
        }
        for space in spaces
    ]


@router.post("/broadcast")
async def broadcast_parking_status(
    db: Session = Depends(get_db)
):
    occupancy_data = get_occupancy_data(db)

    message = {
        "type": "PARKING_UPDATE",
        "data": occupancy_data
    }

    await manager.broadcast(message)

    return {
        "message": "Parking status broadcasted",
        "data": occupancy_data
    }