import cv2

from vision.camera_manager import CameraManager
from vision.parking_space_detector import ParkingSpaceDetector


camera = CameraManager()

detector = ParkingSpaceDetector()

camera.open_camera(0)

print("✅ Camera started.")
print("🅿️ Live parking-space matching started.")
print("Press Q to quit.")


while True:

    frame = camera.read_frame()

    if frame is None:

        print(
            "❌ Could not read camera frame."
        )

        break

    # =====================================================
    # Analyze parking spaces
    # =====================================================

    parking_status = (
        detector.analyze_frame(
            frame
        )
    )

    # =====================================================
    # Calculate summary
    # =====================================================

    summary = (
        detector.get_occupancy_summary(
            parking_status
        )
    )

    # =====================================================
    # Draw parking spaces
    # =====================================================

    for space in parking_status:

        space_config = next(
            item
            for item in detector.parking_spaces
            if item["space_number"]
            == space["space_number"]
        )

        x1 = space_config["x1"]
        y1 = space_config["y1"]

        x2 = space_config["x2"]
        y2 = space_config["y2"]

        # -------------------------------------------------
        # Occupied
        # -------------------------------------------------

        if space["occupied"]:

            box_color = (
                0,
                0,
                255
            )

            status_text = "OCCUPIED"

        # -------------------------------------------------
        # Available
        # -------------------------------------------------

        else:

            box_color = (
                0,
                255,
                0
            )

            status_text = "AVAILABLE"

        # Draw parking box

        cv2.rectangle(
            frame,
            (x1, y1),
            (x2, y2),
            box_color,
            2
        )

        # Space label

        label = (
            f"{space['space_number']} "
            f"{status_text}"
        )

        cv2.putText(
            frame,
            label,
            (x1, y1 - 8),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            box_color,
            2
        )

        # Show overlap when occupied

        if space["occupied"]:

            overlap_text = (
                f"Overlap: "
                f"{space['overlap']:.2f}"
            )

            cv2.putText(
                frame,
                overlap_text,
                (x1, y2 + 18),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.4,
                box_color,
                1
            )

    # =====================================================
    # Display occupancy information
    # =====================================================

    cv2.putText(
        frame,
        (
            f"Total: "
            f"{summary['total_spaces']}"
        ),
        (20, 35),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )

    cv2.putText(
        frame,
        (
            f"Occupied: "
            f"{summary['occupied_spaces']}"
        ),
        (20, 70),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )

    cv2.putText(
        frame,
        (
            f"Available: "
            f"{summary['available_spaces']}"
        ),
        (20, 105),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )

    cv2.putText(
        frame,
        (
            f"Occupancy: "
            f"{summary['occupancy_percentage']:.1f}%"
        ),
        (20, 140),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )

    # =====================================================
    # Show camera
    # =====================================================

    cv2.imshow(
        "AI Parking - Live Space Matching",
        frame
    )

    if cv2.waitKey(1) & 0xFF == ord("q"):

        break


camera.release_camera()

cv2.destroyAllWindows()

print(
    "✅ Live parking-space matching stopped."
)