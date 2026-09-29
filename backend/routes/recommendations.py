from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import ParkingExit

from ai.predictor import predict_congestion
from ai.route_optimizer import find_best_exit

from utils.recommendation_manager import recommendation_manager


router = APIRouter(
    prefix="/api/recommendations",
    tags=["AI Recommendations"]
)


def calculate_recommendation(db: Session):

    exits = db.query(ParkingExit).all()

    exit_data = []

    for parking_exit in exits:

        # Recalculate congestion using current database values
        congestion = predict_congestion(
            queue_length=parking_exit.queue_length,
            waiting_time=parking_exit.waiting_time,
            distance=parking_exit.distance
        )

        # Keep database congestion synchronized
        parking_exit.congestion_level = congestion

        exit_data.append({
            "name": parking_exit.name,
            "queue_length": parking_exit.queue_length,
            "waiting_time": parking_exit.waiting_time,
            "distance": parking_exit.distance,
            "congestion_level": congestion,
            "is_available": parking_exit.is_available
        })

    db.commit()

    recommendation = find_best_exit(exit_data)

    if recommendation is None:
        return {
            "status": "NO_EXIT_AVAILABLE",
            "message": "No parking exit is currently available",
            "recommended_exit": None,
            "alternatives": []
        }

    best_exit = recommendation["recommended_exit"]

    return {
        "status": "SUCCESS",
        "recommended_exit": best_exit,
        "alternatives": recommendation["alternative_exits"]
    }


async def broadcast_recommendation(db: Session):

    recommendation = calculate_recommendation(db)

    message = {
        "type": "AI_EXIT_RECOMMENDATION",
        "data": recommendation
    }

    await recommendation_manager.broadcast(message)

    return recommendation


@router.get("/")
def get_recommendation(
    db: Session = Depends(get_db)
):
    return calculate_recommendation(db)