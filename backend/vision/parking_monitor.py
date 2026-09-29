import cv2

from vision.camera_manager import CameraManager
from vision.parking_space_detector import ParkingSpaceDetector


class ParkingMonitor:

    def __init__(self):

        self.camera = CameraManager()

        self.detector = ParkingSpaceDetector()

    def start(self):

        self.camera.open_camera(0)

        print("✅ Parking camera started.")
        print("🅿️ Real-time parking monitoring started.")
        print("Press Q to stop.")

        while True:

            frame = self.camera.read_frame()

            if frame is None:

                print(
                    "❌ Could not read camera frame."
                )

                break

            parking_status = (
                self.detector.analyze_frame(
                    frame
                )
            )

            occupied_count = sum(
                1
                for space in parking_status
                if space["occupied"]
            )

            total_spaces = len(
                parking_status
            )

            available_count = (
                total_spaces
                -
                occupied_count
            )

            occupancy_percentage = (
                (
                    occupied_count
                    /
                    total_spaces
                )
                * 100
                if total_spaces > 0
                else 0
            )

            # Draw parking spaces
            for space in parking_status:

                config = next(
                    item
                    for item in self.detector.parking_spaces
                    if item["space_number"]
                    == space["space_number"]
                )

                x1 = config["x1"]
                y1 = config["y1"]
                x2 = config["x2"]
                y2 = config["y2"]

                if space["occupied"]:

                    box_color = (
                        0,
                        0,
                        255
                    )

                    status = "OCCUPIED"

                else:

                    box_color = (
                        0,
                        255,
                        0
                    )

                    status = "AVAILABLE"

                cv2.rectangle(
                    frame,
                    (x1, y1),
                    (x2, y2),
                    box_color,
                    2
                )

                cv2.putText(
                    frame,
                    (
                        f"{space['space_number']} "
                        f"{status}"
                    ),
                    (x1, y1 - 8),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.45,
                    box_color,
                    2
                )

            # Dashboard information
            cv2.putText(
                frame,
                f"Total Spaces: {total_spaces}",
                (20, 35),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (255, 255, 255),
                2
            )

            cv2.putText(
                frame,
                f"Occupied: {occupied_count}",
                (20, 65),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (255, 255, 255),
                2
            )

            cv2.putText(
                frame,
                f"Available: {available_count}",
                (20, 95),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (255, 255, 255),
                2
            )

            cv2.putText(
                frame,
                (
                    f"Occupancy: "
                    f"{occupancy_percentage:.1f}%"
                ),
                (20, 125),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (255, 255, 255),
                2
            )

            cv2.imshow(
                "AI Parking - Real-Time Monitor",
                frame
            )

            if (
                cv2.waitKey(1) & 0xFF
                == ord("q")
            ):

                break

        self.stop()

    def stop(self):

        self.camera.release_camera()

        cv2.destroyAllWindows()

        print(
            "✅ Parking monitoring stopped."
        )


if __name__ == "__main__":

    monitor = ParkingMonitor()

    monitor.start()