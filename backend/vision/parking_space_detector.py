from vision.vehicle_detection import VehicleDetector
from vision.parking_spaces import PARKING_SPACES


class ParkingSpaceDetector:

    def __init__(self):

        self.vehicle_detector = VehicleDetector()

        self.parking_spaces = PARKING_SPACES

        # Two detections with this much overlap
        # are treated as the same vehicle.
        self.duplicate_overlap_threshold = 0.40

    # =====================================================
    # CALCULATE OVERLAP BETWEEN TWO BOXES
    # =====================================================

    def calculate_box_overlap(
        self,
        vehicle1,
        vehicle2
    ):

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
            * intersection_height
        )

        area1 = (
            vehicle1["width"]
            * vehicle1["height"]
        )

        area2 = (
            vehicle2["width"]
            * vehicle2["height"]
        )

        smallest_area = min(
            area1,
            area2
        )

        if smallest_area <= 0:

            return 0.0

        return (
            intersection_area
            / smallest_area
        )

    # =====================================================
    # REMOVE DUPLICATE VEHICLE DETECTIONS
    # =====================================================

    def remove_duplicate_vehicles(
        self,
        vehicles
    ):

        if not vehicles:

            return []

        # Highest confidence first.
        vehicles = sorted(
            vehicles,
            key=lambda vehicle:
                vehicle.get(
                    "confidence",
                    0
                ),
            reverse=True
        )

        unique_vehicles = []

        for vehicle in vehicles:

            duplicate = False

            for existing in unique_vehicles:

                # Only compare same vehicle type.
                if (
                    vehicle.get("type")
                    != existing.get("type")
                ):

                    continue

                overlap = (
                    self.calculate_box_overlap(
                        vehicle,
                        existing
                    )
                )

                if (
                    overlap
                    >= self.duplicate_overlap_threshold
                ):

                    duplicate = True

                    break

            if not duplicate:

                unique_vehicles.append(
                    vehicle
                )

        return unique_vehicles

    # =====================================================
    # CALCULATE VEHICLE / PARKING SPACE OVERLAP
    # =====================================================

    def calculate_overlap(
        self,
        space,
        vehicle
    ):

        sx1 = space["x1"]
        sy1 = space["y1"]
        sx2 = space["x2"]
        sy2 = space["y2"]

        vx1 = vehicle["x"]
        vy1 = vehicle["y"]

        vx2 = (
            vx1
            + vehicle["width"]
        )

        vy2 = (
            vy1
            + vehicle["height"]
        )

        intersection_x1 = max(
            sx1,
            vx1
        )

        intersection_y1 = max(
            sy1,
            vy1
        )

        intersection_x2 = min(
            sx2,
            vx2
        )

        intersection_y2 = min(
            sy2,
            vy2
        )

        if (
            intersection_x2
            <= intersection_x1
            or
            intersection_y2
            <= intersection_y1
        ):

            return 0.0

        intersection_area = (
            intersection_x2
            - intersection_x1
        ) * (
            intersection_y2
            - intersection_y1
        )

        space_area = (
            sx2 - sx1
        ) * (
            sy2 - sy1
        )

        if space_area <= 0:

            return 0.0

        return (
            intersection_area
            / space_area
        )

    # =====================================================
    # FIND BEST PARKING SPACE FOR VEHICLE
    # =====================================================

    def find_best_space_for_vehicle(
        self,
        vehicle
    ):

        best_space = None

        highest_overlap = 0.0

        for space in self.parking_spaces:

            overlap = (
                self.calculate_overlap(
                    space,
                    vehicle
                )
            )

            if overlap > highest_overlap:

                highest_overlap = overlap

                best_space = space

        if (
            best_space is not None
            and
            highest_overlap >= 0.20
        ):

            return (
                best_space,
                highest_overlap
            )

        return (
            None,
            highest_overlap
        )

    # =====================================================
    # ANALYZE COMPLETE PARKING AREA
    # =====================================================

    def analyze_frame(
        self,
        frame
    ):

        # -------------------------------------------------
        # Detect vehicles
        # -------------------------------------------------

        vehicles = (
            self.vehicle_detector.detect_vehicles(
                frame
            )
        )

        # -------------------------------------------------
        # Remove duplicate YOLO detections
        # -------------------------------------------------

        vehicles = (
            self.remove_duplicate_vehicles(
                vehicles
            )
        )

        # -------------------------------------------------
        # Initially every space is FREE
        # -------------------------------------------------

        parking_status = []

        for space in self.parking_spaces:

            parking_status.append({

                "space_number":
                    space["space_number"],

                "occupied":
                    False,

                "overlap":
                    0.0,

                "vehicle":
                    None
            })

        # -------------------------------------------------
        # Prevent one space from receiving
        # multiple vehicles
        # -------------------------------------------------

        assigned_spaces = set()

        # -------------------------------------------------
        # Assign each unique vehicle
        # to its best parking space
        # -------------------------------------------------

        for vehicle in vehicles:

            best_space, overlap = (
                self.find_best_space_for_vehicle(
                    vehicle
                )
            )

            if best_space is None:

                continue

            space_number = (
                best_space["space_number"]
            )

            if space_number in assigned_spaces:

                continue

            assigned_spaces.add(
                space_number
            )

            # -------------------------------------------------
            # Update matching space
            # -------------------------------------------------

            for status in parking_status:

                if (
                    status["space_number"]
                    ==
                    space_number
                ):

                    status["occupied"] = True

                    status["overlap"] = round(
                        overlap,
                        2
                    )

                    status["vehicle"] = (
                        vehicle
                    )

                    break

        return parking_status

    # =====================================================
    # GET OCCUPANCY SUMMARY
    # =====================================================

    def get_occupancy_summary(
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

        occupancy_percentage = (

            (
                occupied_spaces
                / total_spaces
            ) * 100

            if total_spaces > 0

            else 0
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
                )
        }