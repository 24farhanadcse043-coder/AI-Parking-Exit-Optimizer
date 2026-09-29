from database import SessionLocal
from models import ParkingSpace

from vision.parking_space_detector import (
    ParkingSpaceDetector
)

from vision.parking_database_updater import (
    update_parking_database
)

import cv2


camera = cv2.VideoCapture(0)

detector = ParkingSpaceDetector()

print("✅ Camera started.")
print("🅿️ Database parking detection started.")
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

    update_parking_database(
        parking_status
    )

    db = SessionLocal()

    try:

        spaces = (
            db.query(ParkingSpace)
            .all()
        )

        occupied = sum(
            1
            for space in spaces
            if space.occupied
        )

        available = (
            len(spaces)
            -
            occupied
        )

        print(
            f"Occupied: {occupied} | "
            f"Available: {available}"
        )

    finally:

        db.close()

    cv2.imshow(
        "AI Parking - Database Detection",
        frame
    )

    if cv2.waitKey(1) & 0xFF == ord("q"):

        break


camera.release()

cv2.destroyAllWindows()

print(
    "✅ Database detection stopped."
)