import cv2

from vision.camera_manager import CameraManager
from vision.live_exit_analyzer import LiveExitAnalyzer


camera = CameraManager()

analyzer = LiveExitAnalyzer()

camera.open_camera(0)

print("✅ Camera started.")
print("🤖 Live AI exit analyzer started.")
print("Press Q to quit.")

while True:

    frame = camera.read_frame()

    if frame is None:

        print("❌ Could not read camera frame.")

        break

    result = analyzer.get_recommendation(frame)

    analysis = result["analysis"]

    recommendation = result["recommendation"]

    vehicles = analysis["vehicles"]

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

    # Exit A information

    exit_a = analysis["exits"]["Exit A"]

    cv2.putText(
        frame,
        f"Exit A Queue: {exit_a['queue_length']}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )

    cv2.putText(
        frame,
        f"Wait: {exit_a['estimated_waiting_time']} min",
        (20, 75),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )

    cv2.putText(
        frame,
        f"AI Traffic: {exit_a['ai_congestion']}",
        (20, 110),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )

    # Recommendation

    if recommendation:

        recommended_exit = recommendation[
            "recommended_exit"
        ]

        cv2.putText(
            frame,
            f"Recommended: {recommended_exit['name']}",
            (20, 150),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 255),
            2
        )

    else:

        cv2.putText(
            frame,
            "No available exit",
            (20, 150),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 0, 255),
            2
        )

    cv2.imshow(
        "AI Parking - Live Exit Analyzer",
        frame
    )

    if cv2.waitKey(1) & 0xFF == ord("q"):

        break


camera.release_camera()

cv2.destroyAllWindows()

print("✅ Live AI exit analyzer stopped.")