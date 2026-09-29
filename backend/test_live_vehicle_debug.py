import cv2

from vision.vehicle_detection import VehicleDetector


print("=" * 60)
print("   PARKAI — LIVE CAMERA VEHICLE DEBUG")
print("=" * 60)


detector = VehicleDetector()

camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("❌ Could not open camera.")
    exit()


print("✅ Camera opened.")

vehicle_classes = {
    2: "car",
    3: "motorcycle",
    5: "bus",
    7: "truck"
}


for frame_number in range(1, 11):

    success, frame = camera.read()

    if not success:
        print(
            f"Frame {frame_number}: "
            "could not read frame."
        )
        continue

    results = detector.model(
        frame,
        imgsz=1280,
        conf=0.05,
        iou=0.45,
        verbose=False
    )

    print(
        f"\n========== FRAME {frame_number} =========="
    )

    object_count = 0
    vehicle_count = 0

    for result in results:

        if result.boxes is None:
            continue

        for box in result.boxes:

            class_id = int(
                box.cls[0].item()
            )

            confidence = float(
                box.conf[0].item()
            )

            class_name = detector.model.names.get(
                class_id,
                str(class_id)
            )

            object_count += 1

            print(
                f"Detected: "
                f"{class_name:<15} "
                f"confidence={confidence:.2f}"
            )

            if class_id in vehicle_classes:
                vehicle_count += 1

    print(
        f"Objects detected: {object_count}"
    )

    print(
        f"Vehicles detected: {vehicle_count}"
    )


camera.release()

print("\n==========================================")
print("LIVE CAMERA DEBUG FINISHED")
print("==========================================")