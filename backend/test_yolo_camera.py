import cv2
from ultralytics import YOLO


# =========================================================
# SETTINGS
# =========================================================

CAMERA_SOURCE = 0
MODEL_FILE = "yolo11n.pt"

CONFIDENCE = 0.15
IMAGE_SIZE = 1280


# =========================================================
# VEHICLE CLASSES
# =========================================================

VEHICLE_CLASSES = {
    2: "car",
    3: "motorcycle",
    5: "bus",
    7: "truck"
}


# =========================================================
# LOAD MODEL
# =========================================================

print()
print("==========================================")
print("     PARKAI — DIRECT CAMERA YOLO TEST")
print("==========================================")
print()

print("Loading YOLO model...")

model = YOLO(
    MODEL_FILE
)

print("✅ YOLO model loaded.")


# =========================================================
# OPEN CAMERA
# =========================================================

print()
print("Opening camera...")

camera = cv2.VideoCapture(
    CAMERA_SOURCE
)

if not camera.isOpened():

    print(
        "❌ Unable to open camera."
    )

    raise SystemExit


print("✅ Camera opened.")
print()


# =========================================================
# READ FRAMES
# =========================================================

for frame_number in range(1, 11):

    success, frame = camera.read()

    if not success:

        print(
            "❌ Unable to read camera frame."
        )

        break


    print(
        f"\n========== FRAME {frame_number} =========="
    )


    # =====================================================
    # YOLO
    # =====================================================

    results = model(
        frame,
        imgsz=IMAGE_SIZE,
        conf=CONFIDENCE,
        iou=0.45,
        verbose=False
    )


    detection_count = 0
    vehicle_count = 0


    # =====================================================
    # PROCESS ALL DETECTIONS
    # =====================================================

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

            class_name = model.names[
                class_id
            ]

            detection_count += 1


            x1, y1, x2, y2 = (
                box.xyxy[0].tolist()
            )


            center_x = (
                x1 + x2
            ) / 2


            center_y = (
                y1 + y2
            ) / 2


            print(
                f"Detected: {class_name:<12} "
                f"confidence={confidence:.2f} "
                f"center=({int(center_x)}, "
                f"{int(center_y)})"
            )


            # -------------------------------------------------
            # Count vehicles
            # -------------------------------------------------

            if class_id in VEHICLE_CLASSES:

                vehicle_count += 1


                print(
                    f"  🚗 VEHICLE TYPE: "
                    f"{VEHICLE_CLASSES[class_id]}"
                )


    # =====================================================
    # FRAME SUMMARY
    # =====================================================

    print(
        f"Objects detected: {detection_count}"
    )

    print(
        f"Vehicles detected: {vehicle_count}"
    )


# =========================================================
# CLEANUP
# =========================================================

camera.release()


print()
print("==========================================")
print("DIRECT CAMERA TEST FINISHED")
print("==========================================")
print()