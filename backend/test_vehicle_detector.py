import cv2

from vision.vehicle_detection import VehicleDetector


VIDEO_PATH = "vehicle_test.mp4"


print("=" * 50)
print("   PARKAI — ACTUAL VEHICLE DETECTOR TEST")
print("=" * 50)


print("\nLoading VehicleDetector...")

detector = VehicleDetector()

print("✅ VehicleDetector loaded.")


print("\nOpening vehicle test video...")

video = cv2.VideoCapture(VIDEO_PATH)

if not video.isOpened():
    print("❌ Could not open vehicle_test.mp4")
    exit()

print("✅ Video opened.")


max_frames = 20

frame_number = 0
frames_with_vehicles = 0
total_vehicles = 0


while frame_number < max_frames:

    success, frame = video.read()

    if not success:
        break

    frame_number += 1

    vehicles = detector.detect_vehicles(frame)

    print(
        f"\nFrame {frame_number:02d}"
    )

    if vehicles:

        frames_with_vehicles += 1

        for vehicle in vehicles:

            print(
                f"Vehicle: {vehicle['type']:<12} "
                f"confidence={vehicle['confidence']:.2f} "
                f"x={vehicle['x']} "
                f"y={vehicle['y']} "
                f"width={vehicle['width']} "
                f"height={vehicle['height']}"
            )

        total_vehicles += len(vehicles)

    else:

        print("No vehicles detected.")


video.release()


print("\n==========================================")
print("ACTUAL VEHICLE DETECTOR TEST FINISHED")
print("==========================================")

print(
    f"Frames processed: {frame_number}"
)

print(
    f"Frames with vehicles: {frames_with_vehicles}"
)

print(
    f"Total vehicle detections: {total_vehicles}"
)


if total_vehicles > 0:

    print(
        "\n✅ PROJECT VEHICLE DETECTOR IS WORKING."
    )

else:

    print(
        "\n❌ PROJECT VEHICLE DETECTOR FOUND NO VEHICLES."
    )