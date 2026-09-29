import cv2
from ultralytics import YOLO

VIDEO_PATH = "vehicle_test.mp4"

print("=" * 50)
print("   PARKAI — CONTINUOUS YOLO VEHICLE TEST")
print("=" * 50)

# ---------------------------------------------------------
# LOAD MODEL
# ---------------------------------------------------------

print("\nLoading YOLO model...")

model = YOLO("yolo11n.pt")

print("✅ YOLO model loaded.")

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
# VEHICLE CLASSES
# ---------------------------------------------------------

vehicle_classes = {
    2: "car",
    3: "motorcycle",
    5: "bus",
    7: "truck"
}

# ---------------------------------------------------------
# PROCESS 20 FRAMES
# ---------------------------------------------------------

MAX_FRAMES = 20

frame_number = 0
frames_with_vehicles = 0
total_vehicle_detections = 0

while frame_number < MAX_FRAMES:

    success, frame = video.read()

    if not success:
        print("\n⚠️ Video ended.")
        break

    frame_number += 1

    results = model(
        frame,
        imgsz=1280,
        conf=0.05,
        iou=0.45,
        verbose=False
    )

    frame_vehicle_count = 0

    for result in results:

        if result.boxes is None:
            continue

        for box in result.boxes:

            class_id = int(box.cls[0].item())

            confidence = float(
                box.conf[0].item()
            )

            if class_id in vehicle_classes:

                vehicle_name = vehicle_classes[class_id]

                frame_vehicle_count += 1
                total_vehicle_detections += 1

                print(
                    f"Frame {frame_number:02d}: "
                    f"{vehicle_name:<12} "
                    f"confidence={confidence:.2f}"
                )

    if frame_vehicle_count > 0:
        frames_with_vehicles += 1

    print(
        f"Frame {frame_number:02d} "
        f"-> Vehicles: {frame_vehicle_count}"
    )

# ---------------------------------------------------------
# CLEANUP
# ---------------------------------------------------------

video.release()

# ---------------------------------------------------------
# FINAL RESULT
# ---------------------------------------------------------

print("\n==========================================")
print("CONTINUOUS YOLO TEST FINISHED")
print("==========================================")

print(f"Frames processed: {frame_number}")

print(
    f"Frames containing vehicles: "
    f"{frames_with_vehicles}"
)

print(
    f"Total vehicle detections: "
    f"{total_vehicle_detections}"
)

if total_vehicle_detections > 0:

    print(
        "\n✅ YOLO is continuously detecting "
        "vehicles from the video."
    )

else:

    print(
        "\n❌ No vehicles detected."
    )