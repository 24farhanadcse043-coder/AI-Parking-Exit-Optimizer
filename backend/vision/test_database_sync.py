import cv2

from vision.parking_space_detector import (
    ParkingSpaceDetector
)

from vision.parking_database_updater import (
    update_parking_database
)


camera = cv2.VideoCapture(0)

if not camera.isOpened():

    print("❌ Camera could not be opened.")

    exit()


detector = ParkingSpaceDetector()

print("✅ Camera started.")
print("🅿️ Parking database synchronization started.")
print("Press Q to quit.")

while True:

    success, frame = camera.read()

    if not success:

        print(
            "❌ Could not read camera frame."
        )

        break

    parking_status = (
        detector.analyze_frame(frame)
    )

    result = update_parking_database(
        parking_status
    )

    occupied_count = sum(
        1
        for space in parking_status
        if space["occupied"]
    )

    available_count = (
        len(parking_status)
        -
        occupied_count
    )

    cv2.putText(
        frame,
        f"Occupied: {occupied_count}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 0),
        2
    )

    cv2.putText(
        frame,
        f"Available: {available_count}",
        (20, 75),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 0),
        2
    )

    cv2.putText(
        frame,
        (
            f"DB Updated: "
            f"{result.get('updated_spaces', 0)}"
        ),
        (20, 110),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2
    )

    cv2.imshow(
        "AI Parking - Database Sync",
        frame
    )

    if cv2.waitKey(1) & 0xFF == ord("q"):

        break


camera.release()

cv2.destroyAllWindows()

print("✅ Database synchronization stopped.")