from vision.vehicle_detection import VehicleDetector
from vision.queue_detection import QueueDetector
from vision.exit_regions import EXIT_REGIONS

from ai.predictor import predict_congestion
from ai.route_optimizer import find_best_exit


class LiveExitAnalyzer:

    def __init__(self):

        self.vehicle_detector = VehicleDetector()

        self.exit_detectors = {}

        for exit_name, region in EXIT_REGIONS.items():

            self.exit_detectors[exit_name] = QueueDetector(
                exit_name=exit_name,
                region=region
            )

    def analyze_frame(self, frame):

        vehicles = self.vehicle_detector.detect_vehicles(
            frame
        )

        exits = {}

        for exit_name, detector in self.exit_detectors.items():

            queue_data = detector.analyze_queue(
                vehicles
            )

            queue_length = queue_data[
                "queue_length"
            ]

            waiting_time = queue_data[
                "estimated_waiting_time"
            ]

            # Use a different approximate distance
            # for each exit.

            if exit_name == "Exit A":
                distance = 100

            elif exit_name == "Exit B":
                distance = 150

            else:
                distance = 200

            ai_congestion = predict_congestion(
                queue_length=queue_length,
                waiting_time=waiting_time,
                distance=distance
            )

            queue_data["ai_congestion"] = (
                ai_congestion
            )

            queue_data["distance"] = distance

            exits[exit_name] = queue_data

        return {
            "vehicles": vehicles,
            "exits": exits
        }

    def get_recommendation(self, frame):

        analysis = self.analyze_frame(frame)

        exit_data = []

        for exit_name, data in analysis[
            "exits"
        ].items():

            exit_data.append({

                "name": exit_name,

                "queue_length":
                    data["queue_length"],

                "waiting_time":
                    data["estimated_waiting_time"],

                "distance":
                    data["distance"],

                "congestion_level":
                    data["ai_congestion"],

                "is_available": True
            })

        recommendation = find_best_exit(
            exit_data
        )

        return {
            "analysis": analysis,
            "recommendation": recommendation
        }