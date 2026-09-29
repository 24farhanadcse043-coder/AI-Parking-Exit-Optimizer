import cv2

from vision.parking_space_detector import ParkingSpaceDetector


VIDEO_PATH = "vehicle_test.mp4"


print("=" * 60)
print("   PARKAI — PARKING OCCUPANCY DETECTOR TEST")
print("=" * 60)


# ---------------------------------------------------------
# LOAD DETECTOR
# ---------------------------------------------------------

print("\nLoading ParkingSpaceDetector...")

detector = ParkingSpaceDetector()

print("✅ ParkingSpaceDetector loaded.")


# ---------------------------------------------------------
# OPEN VIDEO
# ---------------------------------------------------------

print("\nOpening vehicle test video...")

video = cv2.VideoCapture(VIDEO_PATH)

if not video.isOpened():

    print("❌ Could not open vehicle_test.mp4")

    exit()

print("✅ Video opened.")


# ---------------------------------------------------------
# READ FIRST FRAME
# ---------------------------------------------------------

success, frame = video.read()

if not success or frame is None:

    print("❌ Could not read video frame.")

    video.release()

    exit()


height, width = frame.shape[:2]

print(
    f"\nVideo frame size: "
    f"{width} x {height}"
)


# ---------------------------------------------------------
# PARKING LAYOUT SIZE
# ---------------------------------------------------------

print("\nParking spaces:")

for space in detector.parking_spaces:

    print(
        f"{space['space_number']}: "
        f"({space['x1']},{space['y1']}) -> "
        f"({space['x2']},{space['y2']})"
    )


# ---------------------------------------------------------
# ANALYZE FRAME
# ---------------------------------------------------------

print("\nRunning parking occupancy detection...")

parking_status = detector.analyze_frame(frame)


# ---------------------------------------------------------
# DISPLAY RESULTS
# ---------------------------------------------------------

occupied_count = 0


print("\nParking-space results:")

for status in parking_status:

    if status["occupied"]:

        occupied_count += 1

        print(
            f"{status['space_number']}: "
            f"OCCUPIED | "
            f"overlap={status['overlap']} | "
            f"vehicle={status['vehicle']}"
        )

    else:

        print(
            f"{status['space_number']}: FREE | "
            f"overlap={status['overlap']}"
        )


# ---------------------------------------------------------
# SUMMARY
# ---------------------------------------------------------

summary = detector.get_occupancy_summary(
    parking_status
)


print("\n" + "=" * 60)
print("PARKING OCCUPANCY SUMMARY")
print("=" * 60)

print(
    f"Total spaces: "
    f"{summary['total_spaces']}"
)

print(
    f"Occupied spaces: "
    f"{summary['occupied_spaces']}"
)

print(
    f"Available spaces: "
    f"{summary['available_spaces']}"
)

print(
    f"Occupancy: "
    f"{summary['occupancy_percentage']}%"
)


# ---------------------------------------------------------
# CLEANUP
# ---------------------------------------------------------

video.release()


print("\n==========================================")
print("PARKING OCCUPANCY TEST FINISHED")
print("==========================================")