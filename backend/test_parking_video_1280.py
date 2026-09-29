import cv2

from vision.parking_space_detector import ParkingSpaceDetector


VIDEO_PATH = "parking_test_video.mp4"

print("=" * 60)
print("   PARKAI — 1280x720 PARKING VIDEO TEST")
print("=" * 60)

print("\nLoading ParkingSpaceDetector...")

detector = ParkingSpaceDetector()

print("✅ ParkingSpaceDetector loaded.")

print("\nOpening test video...")

video = cv2.VideoCapture(VIDEO_PATH)

if not video.isOpened():
    print("❌ Could not open parking_test_video.mp4")
    exit()

print("✅ Video opened.")

frame_number = 0
max_frames = 10

while frame_number < max_frames:

    success, frame = video.read()

    if not success:
        break

    frame_number += 1

    height, width = frame.shape[:2]

    parking_status = detector.analyze_frame(frame)

    summary = detector.get_occupancy_summary(
        parking_status
    )

    occupied_spaces = [
        status["space_number"]
        for status in parking_status
        if status["occupied"]
    ]

    print(
        f"\nFrame {frame_number:02d}"
    )

    print(
        f"Resolution: {width} x {height}"
    )

    print(
        f"Occupied: {occupied_spaces}"
    )

    print(
        f"Occupied count: "
        f"{summary['occupied_spaces']}"
    )

    print(
        f"Available count: "
        f"{summary['available_spaces']}"
    )

video.release()

print("\n" + "=" * 60)
print("1280x720 PARKING VIDEO TEST FINISHED")
print("=" * 60)

print(
    f"Frames processed: {frame_number}"
)

print(
    "Expected: P001 should be occupied "
    "and most other spaces should be free."
)