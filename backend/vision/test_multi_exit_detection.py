import cv2

from vision.camera_manager import CameraManager
from vision.live_exit_analyzer import LiveExitAnalyzer
from vision.exit_regions import EXIT_REGIONS


camera = CameraManager()

analyzer = LiveExitAnalyzer()

camera.open_camera(0)

print("✅ Camera started.")
print("🚗 Multi-exit queue detection started.")
print("Press Q to quit.")

while True:

    frame = camera.read_frame()

    if frame is None:

        print("❌ Could not read camera frame.")

        break

    result = analyzer.get_recommendation(
        frame
    )

    analysis = result["analysis"]

    recommendation = result[
        "recommendation"
    ]

    # --------------------------------
    # Draw exit regions
    # --------------------------------

    for exit_name, region in EXIT_REGIONS.items():

        x1 = region["x1"]
        y1 = region["y1"]

        x2 = region["x2"]
        y2 = region["y2"]

        cv2.rectangle(
            frame,
            (x1, y1),
            (x2, y2),
            (255, 255, 0),
            2
        )

        cv2.putText(
            frame,
            exit_name,
            (x1 + 10, y1 + 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 0),
            2
        )

    # --------------------------------
    # Draw vehicles
    # --------------------------------

    for vehicle in analysis["vehicles"]:

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

    # --------------------------------
    # Display exit information
    # --------------------------------

    y_position = 40

    for exit_name, data in analysis[
        "exits"
    ].items():

        text = (
            f"{exit_name}: "
            f"Queue={data['queue_length']} | "
            f"Wait={data['estimated_waiting_time']}m | "
            f"Traffic={data['ai_congestion']}"
        )

        cv2.putText(
            frame,
            text,
            (20, y_position),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 255, 255),
            2
        )

        y_position += 30

    # --------------------------------
    # Recommended exit
    # --------------------------------

    if recommendation:

        recommended_exit = (
            recommendation[
                "recommended_exit"
            ]
        )

        recommendation_text = (
            "AI Recommended Exit: "
            + recommended_exit["name"]
        )

        cv2.putText(
            frame,
            recommendation_text,
            (20, y_position + 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 255),
            2
        )

    else:

        cv2.putText(
            frame,
            "No available exit",
            (20, y_position + 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 0, 255),
            2
        )

    cv2.imshow(
        "AI Parking - Multi Exit AI",
        frame
    )

    if cv2.waitKey(1) & 0xFF == ord("q"):

        break


camera.release_camera()

cv2.destroyAllWindows()

print("✅ Multi-exit queue detection stopped.")