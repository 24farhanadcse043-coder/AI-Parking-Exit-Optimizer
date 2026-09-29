import asyncio
import random

from database import SessionLocal
from models import ParkingExit

from ai.predictor import predict_congestion
from routes.recommendations import broadcast_recommendation
from routes.route_guidance import broadcast_vehicle_route


# ---------------------------------------------------------
# Simulator settings
# ---------------------------------------------------------

SIMULATION_INTERVAL = 10


# ---------------------------------------------------------
# Update one parking exit
# ---------------------------------------------------------

def update_exit_traffic(db, parking_exit):

    # Generate realistic queue length
    queue_length = random.randint(0, 45)

    # Generate waiting time based on queue
    waiting_time = round(
        queue_length * random.uniform(0.4, 0.8),
        2
    )

    # Keep distance unchanged
    distance = parking_exit.distance

    # AI predicts congestion
    predicted_congestion = predict_congestion(
        queue_length=queue_length,
        waiting_time=waiting_time,
        distance=distance
    )

    # Update database
    parking_exit.queue_length = queue_length
    parking_exit.waiting_time = waiting_time
    parking_exit.congestion_level = predicted_congestion


# ---------------------------------------------------------
# Run one simulation cycle
# ---------------------------------------------------------

async def run_simulation_cycle():

    db = SessionLocal()

    try:

        exits = (
            db.query(ParkingExit)
            .filter(
                ParkingExit.is_available == True
            )
            .all()
        )

        if not exits:
            return

        # Update every exit
        for parking_exit in exits:

            update_exit_traffic(
                db,
                parking_exit
            )

        db.commit()

        # Refresh database objects
        for parking_exit in exits:
            db.refresh(parking_exit)

        # Broadcast new AI recommendation
        await broadcast_recommendation(db)

        # Update routes for parked vehicles
        from models import Vehicle

        vehicles = (
            db.query(Vehicle)
            .filter(
                Vehicle.status == "PARKED"
            )
            .all()
        )

        for vehicle in vehicles:

            await broadcast_vehicle_route(
                vehicle.vehicle_number,
                db
            )

        print(
            "Parking simulation cycle completed."
        )

        for parking_exit in exits:

            print(
                f"{parking_exit.name}: "
                f"Queue={parking_exit.queue_length}, "
                f"Wait={parking_exit.waiting_time}, "
                f"Congestion={parking_exit.congestion_level}"
            )

    finally:

        db.close()


# ---------------------------------------------------------
# Continuous simulation
# ---------------------------------------------------------

async def start_simulation():

    print(
        "Real-time parking simulation started."
    )

    while True:

        try:

            await run_simulation_cycle()

        except Exception as error:

            print(
                f"Simulation error: {error}"
            )

        await asyncio.sleep(
            SIMULATION_INTERVAL
        )