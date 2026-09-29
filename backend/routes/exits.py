from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import ParkingExit, Vehicle

from ai.predictor import predict_congestion

from routes.recommendations import broadcast_recommendation
from routes.route_guidance import broadcast_vehicle_route


router = APIRouter(
    prefix="/api/exits",
    tags=["Parking Exits"]
)


# --------------------------------------------------
# GET ALL EXITS
# --------------------------------------------------

@router.get("/")
def get_exits(
    db: Session = Depends(get_db)
):

    exits = db.query(ParkingExit).all()

    return [
        {
            "id": exit.id,
            "name": exit.name,
            "queue_length": exit.queue_length,
            "waiting_time": exit.waiting_time,
            "distance": exit.distance,
            "congestion_level": exit.congestion_level,
            "is_available": exit.is_available
        }
        for exit in exits
    ]


# --------------------------------------------------
# UPDATE EXIT TRAFFIC USING AI
# --------------------------------------------------

@router.put("/{exit_id}")
async def update_exit(
    exit_id: int,
    queue_length: int,
    waiting_time: float,
    distance: float,
    db: Session = Depends(get_db)
):

    parking_exit = (
        db.query(ParkingExit)
        .filter(ParkingExit.id == exit_id)
        .first()
    )

    if not parking_exit:
        raise HTTPException(
            status_code=404,
            detail="Exit not found"
        )

    # ----------------------------------------------
    # AI CONGESTION PREDICTION
    # ----------------------------------------------

    predicted_congestion = predict_congestion(
        queue_length=queue_length,
        waiting_time=waiting_time,
        distance=distance
    )

    # ----------------------------------------------
    # UPDATE DATABASE
    # ----------------------------------------------

    parking_exit.queue_length = queue_length
    parking_exit.waiting_time = waiting_time
    parking_exit.distance = distance
    parking_exit.congestion_level = predicted_congestion

    db.commit()
    db.refresh(parking_exit)

    # ----------------------------------------------
    # BROADCAST AI RECOMMENDATION
    # ----------------------------------------------

    await broadcast_recommendation(db)

    # ----------------------------------------------
    # UPDATE ROUTES FOR PARKED VEHICLES
    # ----------------------------------------------

    vehicles = (
        db.query(Vehicle)
        .filter(Vehicle.status == "PARKED")
        .all()
    )

    for vehicle in vehicles:

        await broadcast_vehicle_route(
            vehicle.vehicle_number,
            db
        )

    # ----------------------------------------------
    # RESPONSE
    # ----------------------------------------------

    return {
        "message": "Exit information updated using AI",
        "exit": parking_exit.name,
        "queue_length": parking_exit.queue_length,
        "waiting_time": parking_exit.waiting_time,
        "distance": parking_exit.distance,
        "ai_predicted_congestion": predicted_congestion,
        "is_available": parking_exit.is_available
    }


# --------------------------------------------------
# EMERGENCY BLOCK EXIT
# --------------------------------------------------

@router.put("/{exit_id}/emergency")
async def emergency_exit(
    exit_id: int,
    reason: str = "Emergency",
    db: Session = Depends(get_db)
):

    parking_exit = (
        db.query(ParkingExit)
        .filter(ParkingExit.id == exit_id)
        .first()
    )

    if not parking_exit:
        raise HTTPException(
            status_code=404,
            detail="Exit not found"
        )

    parking_exit.is_available = False

    db.commit()
    db.refresh(parking_exit)

    await broadcast_recommendation(db)

    vehicles = (
        db.query(Vehicle)
        .filter(Vehicle.status == "PARKED")
        .all()
    )

    for vehicle in vehicles:

        await broadcast_vehicle_route(
            vehicle.vehicle_number,
            db
        )

    return {
        "status": "EMERGENCY_EXIT_BLOCKED",
        "message": "Parking exit has been blocked due to emergency",
        "exit": parking_exit.name,
        "reason": reason,
        "is_available": parking_exit.is_available
    }


# --------------------------------------------------
# CLEAR EMERGENCY
# --------------------------------------------------

@router.put("/{exit_id}/clear-emergency")
async def clear_emergency(
    exit_id: int,
    db: Session = Depends(get_db)
):

    parking_exit = (
        db.query(ParkingExit)
        .filter(ParkingExit.id == exit_id)
        .first()
    )

    if not parking_exit:
        raise HTTPException(
            status_code=404,
            detail="Exit not found"
        )

    parking_exit.is_available = True

    db.commit()
    db.refresh(parking_exit)

    await broadcast_recommendation(db)

    vehicles = (
        db.query(Vehicle)
        .filter(Vehicle.status == "PARKED")
        .all()
    )

    for vehicle in vehicles:

        await broadcast_vehicle_route(
            vehicle.vehicle_number,
            db
        )

    return {
        "status": "EMERGENCY_CLEARED",
        "message": "Parking exit is available again",
        "exit": parking_exit.name,
        "is_available": parking_exit.is_available
    }