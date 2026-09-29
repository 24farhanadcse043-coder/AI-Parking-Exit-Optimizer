import time


class QueueDetector:

    def __init__(
        self,
        exit_name="Exit A",
        region=None
    ):
        self.exit_name = exit_name
        self.region = region
        self.vehicle_history = []
        self.last_update_time = time.time()

    def is_vehicle_in_region(self, vehicle):

        if self.region is None:
            return True

        x1 = self.region["x1"]
        y1 = self.region["y1"]
        x2 = self.region["x2"]
        y2 = self.region["y2"]

        vehicle_center_x = (
            vehicle["x"] + vehicle["width"] / 2
        )

        vehicle_center_y = (
            vehicle["y"] + vehicle["height"] / 2
        )

        return (
            x1 <= vehicle_center_x <= x2
            and
            y1 <= vehicle_center_y <= y2
        )

    def get_queue_vehicles(self, vehicles):

        queue_vehicles = []

        for vehicle in vehicles:

            if self.is_vehicle_in_region(vehicle):

                queue_vehicles.append(vehicle)

        return queue_vehicles

    def calculate_queue_length(self, vehicles):

        return len(vehicles)

    def estimate_waiting_time(self, queue_length):

        service_time = 15

        waiting_time_seconds = (
            queue_length * service_time
        )

        waiting_time_minutes = (
            waiting_time_seconds / 60
        )

        return round(
            waiting_time_minutes,
            2
        )

    def calculate_congestion(self, queue_length):

        if queue_length <= 5:
            return "LOW"

        elif queue_length <= 10:
            return "MEDIUM"

        return "HIGH"

    def analyze_queue(self, vehicles):

        queue_vehicles = self.get_queue_vehicles(
            vehicles
        )

        queue_length = self.calculate_queue_length(
            queue_vehicles
        )

        waiting_time = self.estimate_waiting_time(
            queue_length
        )

        congestion = self.calculate_congestion(
            queue_length
        )

        result = {
            "exit": self.exit_name,
            "queue_length": queue_length,
            "estimated_waiting_time": waiting_time,
            "congestion": congestion,
            "vehicles": queue_vehicles
        }

        self.vehicle_history.append(result)

        if len(self.vehicle_history) > 20:

            self.vehicle_history.pop(0)

        self.last_update_time = time.time()

        return result