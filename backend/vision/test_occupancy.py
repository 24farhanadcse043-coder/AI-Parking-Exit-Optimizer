import cv2

from vision.camera_manager import CameraManager
from vision.occupancy_detector import OccupancyDetector


camera = CameraManager()
occupancy_detector = OccupancyDetector()

camera.open_camera(0)

print("✅ Camera started.")
print("🅿️ Parking occupancy detection started.")
print("Press Q to quit.")

while True:

    frame = camera.read_frame()

    if frame is None:
        print("❌ Could not read camera frame.")
        break

    result = occupancy_detector.analyze_frame(
        frame
    )

    vehicle_count = result["vehicle_count"]

    vehicle_types = result["vehicle_types"]

    status = (
        "OCCUPIED"
        if result["occupied"]
        else "AVAILABLE"
    )

    cv2.putText(
        frame,
        f"Parking: {status}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 0),
        2
    )

    cv2.putText(
        frame,
        f"Vehicles: {vehicle_count}",
        (20, 75),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2
    )

    cv2.putText(
        frame,
        (
            f"Cars: {vehicle_types['car']} | "
            f"Bikes: {vehicle_types['motorcycle']}"
        ),
        (20, 110),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (0, 255, 0),
        2
    )

    cv2.imshow(
        "AI Parking - Occupancy Detection",
        frame
    )

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


camera.release_camera()
cv2.destroyAllWindows()

print("✅ Occupancy detection stopped.")