import cv2

from vision.camera_manager import CameraManager
from vision.vehicle_detection import VehicleDetector


camera = CameraManager()
detector = VehicleDetector()

camera.open_camera(0)

print("✅ Camera started.")
print("🚗 YOLO vehicle detection started.")
print("Press Q to quit.")

while True:

    frame = camera.read_frame()

    if frame is None:
        print("❌ Could not read camera frame.")
        break

    # Run YOLO only once
    vehicles = detector.detect_vehicles(frame)

    # Calculate counts from the existing detections
    counts = detector.get_vehicle_counts(
        vehicles
    )

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

        label = (
            f"{vehicle_type} "
            f"{confidence:.2f}"
        )

        cv2.putText(
            frame,
            label,
            (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            2
        )

    # Total vehicle count
    cv2.putText(
        frame,
        f"Vehicles: {counts['total']}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 0),
        2
    )

    # Vehicle type counts
    count_text = (
        f"Cars: {counts['car']} | "
        f"Bikes: {counts['motorcycle']} | "
        f"Buses: {counts['bus']} | "
        f"Trucks: {counts['truck']}"
    )

    cv2.putText(
        frame,
        count_text,
        (20, 75),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (0, 255, 0),
        2
    )

    cv2.imshow(
        "AI Parking - YOLO Vehicle Detection",
        frame
    )

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


camera.release_camera()
cv2.destroyAllWindows()

print("✅ Vehicle detection stopped.")