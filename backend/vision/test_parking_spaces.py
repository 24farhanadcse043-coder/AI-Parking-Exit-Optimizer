import cv2

from vision.camera_manager import CameraManager
from vision.parking_space_detector import ParkingSpaceDetector


camera = CameraManager()

detector = ParkingSpaceDetector()

camera.open_camera(0)

print("✅ Camera started.")
print("🅿️ Parking-space detection started.")
print("Press Q to quit.")

while True:

    frame = camera.read_frame()

    if frame is None:
        print("❌ Could not read camera frame.")
        break

    parking_status = detector.analyze_frame(
        frame
    )

    occupied_count = 0

    for space in parking_status:

        space_number = space["space_number"]

        x1 = next(
            item["x1"]
            for item in detector.parking_spaces
            if item["space_number"] == space_number
        )

        y1 = next(
            item["y1"]
            for item in detector.parking_spaces
            if item["space_number"] == space_number
        )

        x2 = next(
            item["x2"]
            for item in detector.parking_spaces
            if item["space_number"] == space_number
        )

        y2 = next(
            item["y2"]
            for item in detector.parking_spaces
            if item["space_number"] == space_number
        )

        if space["occupied"]:

            occupied_count += 1

            box_color = (
                0,
                0,
                255
            )

            status_text = "OCCUPIED"

        else:

            box_color = (
                0,
                255,
                0
            )

            status_text = "AVAILABLE"

        cv2.rectangle(
            frame,
            (x1, y1),
            (x2, y2),
            box_color,
            2
        )

        cv2.putText(
            frame,
            f"{space_number}: {status_text}",
            (x1, y1 - 8),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            box_color,
            2
        )

    total_spaces = len(
        detector.parking_spaces
    )

    available_count = (
        total_spaces
        -
        occupied_count
    )

    cv2.putText(
        frame,
        f"Occupied: {occupied_count}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 255),
        2
    )

    cv2.putText(
        frame,
        f"Available: {available_count}",
        (20, 75),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 255),
        2
    )

    cv2.imshow(
        "AI Parking - Parking Spaces",
        frame
    )

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


camera.release_camera()

cv2.destroyAllWindows()

print("✅ Parking-space detection stopped.")