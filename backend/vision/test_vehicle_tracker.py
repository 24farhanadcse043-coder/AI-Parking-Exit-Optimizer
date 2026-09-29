import cv2

from vision.camera_manager import CameraManager
from vision.vehicle_detection import VehicleDetector
from vision.vehicle_tracker import VehicleTracker


camera = CameraManager()
vehicle_detector = VehicleDetector()
vehicle_tracker = VehicleTracker()

camera.open_camera(0)

print("✅ Camera started.")
print("🚗 Vehicle entry/exit tracking started.")
print("Press Q to quit.")

while True:

    frame = camera.read_frame()

    if frame is None:
        print("❌ Could not read camera frame.")
        break

    # Detect vehicles
    vehicles = vehicle_detector.detect_vehicles(frame)

    # Update tracker
    statistics = vehicle_tracker.update(vehicles)

    # Draw detected vehicles
    for vehicle in vehicles:

        x = vehicle["x"]
        y = vehicle["y"]
        width = vehicle["width"]
        height = vehicle["height"]

        vehicle_type = vehicle["type"]
        confidence = vehicle["confidence"]

        cv2.rectangle(
            frame,
            (x, y),
            (x + width, y + height),
            (0, 255, 0),
            2
        )

        label = f"{vehicle_type} {confidence:.2f}"

        cv2.putText(
            frame,
            label,
            (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            2
        )

    # Display statistics
    cv2.putText(
        frame,
        f"Active Vehicles: {statistics['active_vehicles']}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )

    cv2.putText(
        frame,
        f"Total Entries: {statistics['total_entries']}",
        (20, 75),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )

    cv2.putText(
        frame,
        f"Total Exits: {statistics['total_exits']}",
        (20, 110),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )

    cv2.imshow(
        "AI Parking - Vehicle Entry Exit Tracking",
        frame
    )

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


camera.release_camera()
cv2.destroyAllWindows()

print("✅ Vehicle tracking stopped.")
print()
print("Final statistics:")
print(vehicle_tracker.get_statistics())