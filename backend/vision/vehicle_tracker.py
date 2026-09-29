import time
import math


class VehicleTracker:

    def __init__(self):

        self.active_vehicles = {}

        self.total_entries = 0
        self.total_exits = 0

        self.next_vehicle_id = 1

        # Maximum center movement allowed
        # for matching a vehicle between frames.
        self.max_match_distance = 200

        # Detection overlap threshold used
        # to remove duplicate detections.
        self.duplicate_overlap_threshold = 0.40

    # =========================================================
    # CENTER
    # =========================================================

    def calculate_center(self, vehicle):

        return (
            vehicle["x"] + vehicle["width"] / 2,
            vehicle["y"] + vehicle["height"] / 2
        )

    # =========================================================
    # DISTANCE
    # =========================================================

    def calculate_distance(self, point1, point2):

        return math.sqrt(
            (point1[0] - point2[0]) ** 2
            +
            (point1[1] - point2[1]) ** 2
        )

    # =========================================================
    # IOU / OVERLAP
    # =========================================================

    def calculate_overlap_ratio(self, vehicle1, vehicle2):

        x1 = max(
            vehicle1["x"],
            vehicle2["x"]
        )

        y1 = max(
            vehicle1["y"],
            vehicle2["y"]
        )

        x2 = min(
            vehicle1["x"] + vehicle1["width"],
            vehicle2["x"] + vehicle2["width"]
        )

        y2 = min(
            vehicle1["y"] + vehicle1["height"],
            vehicle2["y"] + vehicle2["height"]
        )

        intersection_width = max(
            0,
            x2 - x1
        )

        intersection_height = max(
            0,
            y2 - y1
        )

        intersection_area = (
            intersection_width
            *
            intersection_height
        )

        area1 = (
            vehicle1["width"]
            *
            vehicle1["height"]
        )

        area2 = (
            vehicle2["width"]
            *
            vehicle2["height"]
        )

        smallest_area = min(
            area1,
            area2
        )

        if smallest_area <= 0:
            return 0.0

        return intersection_area / smallest_area

    # =========================================================
    # REMOVE DUPLICATE DETECTIONS
    # =========================================================

    def remove_duplicate_detections(
        self,
        detected_vehicles
    ):

        if not detected_vehicles:
            return []

        # Highest confidence first.
        sorted_vehicles = sorted(
            detected_vehicles,
            key=lambda vehicle: vehicle.get(
                "confidence",
                0
            ),
            reverse=True
        )

        unique_vehicles = []

        for vehicle in sorted_vehicles:

            is_duplicate = False

            for existing in unique_vehicles:

                # Only compare the same vehicle type.
                if (
                    vehicle.get("type")
                    != existing.get("type")
                ):
                    continue

                overlap = (
                    self.calculate_overlap_ratio(
                        vehicle,
                        existing
                    )
                )

                if (
                    overlap
                    >= self.duplicate_overlap_threshold
                ):

                    is_duplicate = True
                    break

            if not is_duplicate:

                unique_vehicles.append(
                    vehicle
                )

        return unique_vehicles

    # =========================================================
    # VEHICLE ID
    # =========================================================

    def generate_vehicle_id(self):

        vehicle_id = (
            f"VEHICLE_{self.next_vehicle_id:04d}"
        )

        self.next_vehicle_id += 1

        return vehicle_id

    # =========================================================
    # FIND MATCHING VEHICLE
    # =========================================================

    def find_matching_vehicle(self, vehicle):

        current_center = (
            self.calculate_center(vehicle)
        )

        best_match = None

        best_distance = float("inf")

        for (
            vehicle_id,
            tracked
        ) in self.active_vehicles.items():

            previous_center = (
                tracked["center_x"],
                tracked["center_y"]
            )

            distance = (
                self.calculate_distance(
                    current_center,
                    previous_center
                )
            )

            if (
                distance
                < self.max_match_distance
                and
                distance
                < best_distance
            ):

                best_distance = distance

                best_match = vehicle_id

        return best_match

    # =========================================================
    # UPDATE TRACKING
    # =========================================================

    def update(self, detected_vehicles):

        current_time = time.time()

        # Remove duplicate detections first.
        detected_vehicles = (
            self.remove_duplicate_detections(
                detected_vehicles
            )
        )

        matched_ids = set()

        # -----------------------------------------------------
        # PROCESS DETECTIONS
        # -----------------------------------------------------

        for vehicle in detected_vehicles:

            vehicle_id = (
                self.find_matching_vehicle(
                    vehicle
                )
            )

            center_x, center_y = (
                self.calculate_center(
                    vehicle
                )
            )

            # -------------------------------------------------
            # NEW VEHICLE
            # -------------------------------------------------

            if vehicle_id is None:

                vehicle_id = (
                    self.generate_vehicle_id()
                )

                self.active_vehicles[
                    vehicle_id
                ] = {

                    "vehicle_id":
                        vehicle_id,

                    "type":
                        vehicle.get(
                            "type",
                            "vehicle"
                        ),

                    "center_x":
                        center_x,

                    "center_y":
                        center_y,

                    "first_seen":
                        current_time,

                    "last_seen":
                        current_time,

                    "status":
                        "ACTIVE"
                }

                self.total_entries += 1

            # -------------------------------------------------
            # EXISTING VEHICLE
            # -------------------------------------------------

            else:

                tracked = (
                    self.active_vehicles[
                        vehicle_id
                    ]
                )

                tracked["center_x"] = (
                    center_x
                )

                tracked["center_y"] = (
                    center_y
                )

                tracked["last_seen"] = (
                    current_time
                )

                tracked["status"] = (
                    "ACTIVE"
                )

            matched_ids.add(
                vehicle_id
            )

        # -----------------------------------------------------
        # FIND DISAPPEARED VEHICLES
        # -----------------------------------------------------

        disappeared = []

        for vehicle_id in list(
            self.active_vehicles.keys()
        ):

            if vehicle_id in matched_ids:
                continue

            tracked = (
                self.active_vehicles[
                    vehicle_id
                ]
            )

            time_missing = (
                current_time
                -
                tracked["last_seen"]
            )

            if time_missing > 3:

                tracked["status"] = (
                    "EXITED"
                )

                self.total_exits += 1

                disappeared.append(
                    vehicle_id
                )

        # -----------------------------------------------------
        # REMOVE EXITED VEHICLES
        # -----------------------------------------------------

        for vehicle_id in disappeared:

            del self.active_vehicles[
                vehicle_id
            ]

        return self.get_statistics()

    # =========================================================
    # STATISTICS
    # =========================================================

    def get_statistics(self):

        return {

            "active_vehicles":
                len(
                    self.active_vehicles
                ),

            "total_entries":
                self.total_entries,

            "total_exits":
                self.total_exits
        }

    # =========================================================
    # ACTIVE VEHICLES
    # =========================================================

    def get_active_vehicles(self):

        return list(
            self.active_vehicles.values()
        )