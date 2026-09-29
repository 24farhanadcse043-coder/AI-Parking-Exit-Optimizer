import asyncio

from database import SessionLocal
from models import ParkingSpace

from vision.parking_space_detector import ParkingSpaceDetector
from vision.vehicle_tracker import VehicleTracker

from utils.websocket_manager import manager
from utils.dashboard_manager import dashboard_manager


class VisionParkingSync:

    def __init__(self, camera):

        self.camera = camera

        # Parking-space detector
        self.detector = ParkingSpaceDetector()

        # Vehicle tracker
        self.tracker = VehicleTracker()

        self.running = False

        # Latest parking occupancy
        self.last_occupancy = {
            "total_spaces": 0,
            "occupied_spaces": 0,
            "available_spaces": 0,
            "occupancy_percentage": 0.0,
            "spaces": {}
        }

        # Latest vehicle tracking information
        self.last_tracking = {
            "active_vehicles": 0,
            "total_entries": 0,
            "total_exits": 0
        }

    # =====================================================
    # READ SHARED CAMERA
    # =====================================================

    def read_frame(self):

        return self.camera.read()

    # =====================================================
    # UPDATE DATABASE
    # =====================================================

    def update_database(
        self,
        parking_status
    ):

        db = SessionLocal()

        try:

            updated_spaces = 0

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

                # -----------------------------------------
                # Update occupancy
                # -----------------------------------------

                space.occupied = bool(
                    status["occupied"]
                )

                # -----------------------------------------
                # Store detected vehicle marker
                # -----------------------------------------

                vehicle = status.get(
                    "vehicle"
                )

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

                updated_spaces += 1

            db.commit()

            return updated_spaces

        except Exception as error:

            db.rollback()

            print(
                f"❌ Vision database error: "
                f"{error}"
            )

            return 0

        finally:

            db.close()

    # =====================================================
    # CALCULATE OCCUPANCY
    # =====================================================

    def get_occupancy_data(
        self,
        parking_status
    ):

        total_spaces = len(
            parking_status
        )

        occupied_spaces = sum(
            1
            for space in parking_status
            if space["occupied"]
        )

        available_spaces = (
            total_spaces
            - occupied_spaces
        )

        if total_spaces > 0:

            occupancy_percentage = (
                (
                    occupied_spaces
                    / total_spaces
                ) * 100
            )

        else:

            occupancy_percentage = 0

        # -------------------------------------------------
        # INDIVIDUAL PARKING SPACE STATUS
        # -------------------------------------------------

        spaces = {}

        for space in parking_status:

            space_number = (
                space["space_number"]
            )

            spaces[space_number] = bool(
                space["occupied"]
            )

        return {

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
                ),

            "spaces":
                spaces
        }

    # =====================================================
    # BROADCAST LIVE OCCUPANCY
    # =====================================================

    async def broadcast_update(
        self,
        occupancy_data,
        tracking_data
    ):

        # -----------------------------------------
        # Parking WebSocket
        # -----------------------------------------

        parking_message = {
            "type": "PARKING_VISION_UPDATE",
            "data": {
                "occupancy": occupancy_data,
                "vehicle_tracking": tracking_data
            }
        }

        await manager.broadcast(
            parking_message
        )

        # -----------------------------------------
        # Dashboard WebSocket
        # -----------------------------------------

        dashboard_message = {
            "type": "DASHBOARD_UPDATE",
            "data": {
                "parking": occupancy_data,
                "vehicle_tracking": tracking_data
            }
        }

        await dashboard_manager.broadcast(
            dashboard_message
        )

    # =====================================================
    # PROCESS ONE CAMERA FRAME
    # =====================================================

    async def process_frame(
        self,
        frame
    ):

        if frame is None:

            return None

        # -----------------------------------------
        # Detect parking occupancy
        # -----------------------------------------

        parking_status = (
            self.detector.analyze_frame(
                frame
            )
        )

        # -----------------------------------------
        # Collect detected vehicles
        # -----------------------------------------

        detected_vehicles = []

        for status in parking_status:

            vehicle = status.get(
                "vehicle"
            )

            if vehicle:

                detected_vehicles.append(
                    vehicle
                )

        # -----------------------------------------
        # Track vehicles
        # -----------------------------------------

        tracking_data = (
            self.tracker.update(
                detected_vehicles
            )
        )

        # Store latest tracking result
        self.last_tracking = tracking_data

        # -----------------------------------------
        # Update SQLite database
        # -----------------------------------------

        updated_spaces = (
            self.update_database(
                parking_status
            )
        )

        # -----------------------------------------
        # Calculate occupancy
        # -----------------------------------------

        occupancy_data = (
            self.get_occupancy_data(
                parking_status
            )
        )

        # Store latest occupancy
        self.last_occupancy = occupancy_data

        # -----------------------------------------
        # Broadcast live result
        # -----------------------------------------

        await self.broadcast_update(
            occupancy_data,
            tracking_data
        )

        # -----------------------------------------
        # Return complete result
        # -----------------------------------------

        return {

            "parking_status":
                parking_status,

            "occupancy":
                occupancy_data,

            "vehicle_tracking":
                tracking_data,

            "updated_spaces":
                updated_spaces
        }

    # =====================================================
    # START LIVE SYNCHRONIZATION
    # =====================================================

    async def run(self):

        self.running = True

        print(
            "🅿️ Automatic vision parking "
            "synchronization started."
        )

        try:

            while self.running:

                # -----------------------------------------
                # Read shared camera
                # -----------------------------------------

                frame = self.read_frame()

                if frame is None:

                    print(
                        "⚠️ Shared camera frame "
                        "unavailable."
                    )

                    await asyncio.sleep(
                        1
                    )

                    continue

                # -----------------------------------------
                # Process camera frame
                # -----------------------------------------

                await self.process_frame(
                    frame
                )

                # -----------------------------------------
                # Prevent excessive processing
                # -----------------------------------------

                await asyncio.sleep(
                    2
                )

        except asyncio.CancelledError:

            print(
                "🅿️ Parking vision task "
                "cancelled."
            )

        except Exception as error:

            print(
                f"❌ Parking vision error: "
                f"{error}"
            )

        finally:

            self.running = False

    # =====================================================
    # GET LATEST OCCUPANCY
    # =====================================================

    def get_latest_occupancy(self):

        return self.last_occupancy

    # =====================================================
    # GET LATEST VEHICLE TRACKING
    # =====================================================

    def get_latest_tracking(self):

        return self.last_tracking

    # =====================================================
    # STOP VISION SYNCHRONIZATION
    # =====================================================

    def stop(self):

        self.running = False

        print(
            "🅿️ Vision parking "
            "synchronization stopped."
        )