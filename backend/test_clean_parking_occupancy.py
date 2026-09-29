import cv2

from vision.parking_space_detector import ParkingSpaceDetector


IMAGE_PATH = "parking_test_frame.jpg"


print("=" * 60)
print("   PARKAI — CLEAN PARKING OCCUPANCY TEST")
print("=" * 60)


# ---------------------------------------------------------
# LOAD IMAGE
# ---------------------------------------------------------

print("\nLoading parking test image...")

frame = cv2.imread(IMAGE_PATH)

if frame is None:
    print("❌ Could not load parking_test_frame.jpg")
    exit()

height, width = frame.shape[:2]

print("✅ Test image loaded.")
print(f"Image size: {width} x {height}")


# ---------------------------------------------------------
# LOAD PARKING DETECTOR
# ---------------------------------------------------------

print("\nLoading ParkingSpaceDetector...")

detector = ParkingSpaceDetector()

print("✅ ParkingSpaceDetector loaded.")


# ---------------------------------------------------------
# ANALYZE FRAME
# ---------------------------------------------------------

print("\nRunning parking occupancy detection...")

parking_status = detector.analyze_frame(frame)


# ---------------------------------------------------------
# SHOW RESULTS
# ---------------------------------------------------------

print("\nParking-space results:")

for status in parking_status:

    vehicle = status.get("vehicle")

    if status["occupied"]:

        vehicle_type = "unknown"

        confidence = 0.0

        if vehicle:

            vehicle_type = vehicle.get(
                "type",
                "unknown"
            )

            confidence = vehicle.get(
                "confidence",
                0.0
            )

        print(
            f"{status['space_number']}: "
            f"OCCUPIED | "
            f"overlap={status['overlap']} | "
            f"vehicle={vehicle_type} | "
            f"confidence={confidence:.2f}"
        )

    else:

        print(
            f"{status['space_number']}: "
            f"FREE | "
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
# EXPECTED RESULT
# ---------------------------------------------------------

print("\nExpected for this test:")

print("P001 should be OCCUPIED.")

print("Most other spaces should be FREE.")


print("\n==========================================")
print("CLEAN PARKING OCCUPANCY TEST FINISHED")
print("==========================================")