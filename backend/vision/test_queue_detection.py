import cv2

from vision.camera_manager import CameraManager
from vision.vehicle_detection import VehicleDetector
from vision.queue_detection import QueueDetector


camera = CameraManager()

vehicle_detector = VehicleDetector()

queue_detector = QueueDetector(
    exit_name="Exit A"
)

camera.open_camera(0)

print("✅ Camera started.")
print("🚗 Exit queue detection started.")
print("Press Q to quit.")

while True:

    frame = camera.read_frame()

    if frame is None:

        print(
            "❌ Could not read camera frame."
        )

        break

    # Detect vehicles
    vehicles = (
        vehicle_detector
        .detect_vehicles(frame)
    )

    # Analyze queue
    queue_data = (
        queue_detector
        .analyze_queue(vehicles)
    )

    queue_length = (
        queue_data["queue_length"]
    )

    waiting_time = (
        queue_data[
            "estimated_waiting_time"
        ]
    )

    congestion = (
        queue_data["congestion"]
    )

    # Draw detected vehicles
    for vehicle in vehicles:

        x = vehicle["x"]
        y = vehicle["y"]

        width = vehicle["width"]
        height = vehicle["height"]

        vehicle_type = (
            vehicle["type"]
        )

        confidence = (
            vehicle["confidence"]
        )

        cv2.rectangle(
            frame,
            (x, y),
            (
                x + width,
                y + height
            ),
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

    # Queue information
    cv2.putText(
        frame,
        f"Exit: {queue_data['exit']}",
        (20, 35),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )

    cv2.putText(
        frame,
        f"Queue: {queue_length}",
        (20, 70),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )

    cv2.putText(
        frame,
        f"Wait: {waiting_time} min",
        (20, 105),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )

    cv2.putText(
        frame,
        f"Traffic: {congestion}",
        (20, 140),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )

    cv2.imshow(
        "AI Parking - Exit Queue Detection",
        frame
    )

    if cv2.waitKey(1) & 0xFF == ord("q"):

        break


camera.release_camera()

cv2.destroyAllWindows()

print(
    "✅ Exit queue detection stopped."
)