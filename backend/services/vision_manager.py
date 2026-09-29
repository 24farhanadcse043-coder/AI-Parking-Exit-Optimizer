import asyncio

from database import SessionLocal
from models import ParkingExit

from vision.live_exit_analyzer import LiveExitAnalyzer

from utils.recommendation_manager import recommendation_manager
from utils.dashboard_manager import dashboard_manager


class VisionManager:

    def __init__(self, camera):

        self.camera = camera

        self.analyzer = LiveExitAnalyzer()

        self.running = False

        self.latest_result = {
            "status": "WAITING",
            "analysis": {},
            "recommendation": None
        }

    async def process_frame(self, frame):

        if frame is None:
            return None

        try:

            # -----------------------------------------
            # 1. Analyze camera frame
            # -----------------------------------------

            result = self.analyzer.get_recommendation(frame)

            analysis = result["analysis"]
            recommendation = result["recommendation"]

            # -----------------------------------------
            # 2. Update SQLite exit information
            # -----------------------------------------

            db = SessionLocal()

            try:

                for exit_name, exit_data in analysis["exits"].items():

                    parking_exit = (
                        db.query(ParkingExit)
                        .filter(
                            ParkingExit.name == exit_name
                        )
                        .first()
                    )

                    if not parking_exit:
                        continue

                    parking_exit.queue_length = (
                        exit_data["queue_length"]
                    )

                    parking_exit.waiting_time = (
                        exit_data["estimated_waiting_time"]
                    )

                    parking_exit.distance = (
                        exit_data["distance"]
                    )

                    parking_exit.congestion_level = (
                        exit_data["ai_congestion"]
                    )

                db.commit()

            except Exception as error:

                db.rollback()

                print(
                    f"❌ Exit database update error: {error}"
                )

            finally:

                db.close()

            # -----------------------------------------
            # 3. Save latest AI result
            # -----------------------------------------

            self.latest_result = {

                "status": "ACTIVE",

                "analysis": analysis,

                "recommendation": recommendation

            }

            # -----------------------------------------
            # 4. Broadcast AI recommendation
            # -----------------------------------------

            if recommendation:

                recommendation_message = {

                    "type": "AI_EXIT_RECOMMENDATION",

                    "data": recommendation

                }

                await recommendation_manager.broadcast(
                    recommendation_message
                )

            # -----------------------------------------
            # 5. Broadcast dashboard update
            # -----------------------------------------

            dashboard_message = {

                "type": "VISION_EXIT_UPDATE",

                "data": {

                    "analysis": analysis,

                    "recommendation": recommendation

                }

            }

            await dashboard_manager.broadcast(
                dashboard_message
            )

            return self.latest_result

        except Exception as error:

            print(
                f"❌ Vision AI processing error: {error}"
            )

            return None

    async def run(self):

        self.running = True

        print(
            "🤖 Live vision AI processing started."
        )

        try:

            while self.running:

                # -----------------------------------------
                # Get frame from shared camera
                # -----------------------------------------

                frame = self.camera.read()

                if frame is None:

                    print(
                        "⚠️ Shared camera frame unavailable."
                    )

                    await asyncio.sleep(1)

                    continue

                # -----------------------------------------
                # Process frame
                # -----------------------------------------

                await self.process_frame(frame)

                # -----------------------------------------
                # Prevent blocking FastAPI
                # -----------------------------------------

                await asyncio.sleep(2)

        except asyncio.CancelledError:

            print(
                "🤖 Vision manager task cancelled."
            )

        except Exception as error:

            print(
                f"❌ Vision manager error: {error}"
            )

        finally:

            self.running = False

            print(
                "🤖 Vision manager stopped."
            )

    def get_latest_result(self):

        return self.latest_result

    def stop(self):

        self.running = False

        print(
            "🤖 Vision manager stopping..."
        )