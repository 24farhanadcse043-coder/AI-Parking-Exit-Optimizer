from vision.vehicle_detection import VehicleDetector


class OccupancyDetector:

    def __init__(self):

        self.vehicle_detector = VehicleDetector()

    def analyze_frame(self, frame):

        vehicles = self.vehicle_detector.detect_vehicles(
            frame
        )

        vehicle_count = len(vehicles)

        vehicle_counts = (
            self.vehicle_detector.get_vehicle_counts(
                frame
            )
        )

        return {
            "occupied": vehicle_count > 0,
            "vehicle_count": vehicle_count,
            "vehicle_types": vehicle_counts,
            "vehicles": vehicles
        }