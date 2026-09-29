from ultralytics import YOLO
import cv2

print("=" * 50)
print("   PARKAI — YOLO VEHICLE IMAGE TEST")
print("=" * 50)

print("\nLoading YOLO model...")
model = YOLO("yolo11n.pt")
print("✅ YOLO model loaded.")

print("\nLoading vehicle image...")
image = cv2.imread("bus.jpg")

if image is None:
    print("❌ Could not load bus.jpg")
    exit()

print("✅ Vehicle image loaded.")

print("\nRunning YOLO detection...")

results = model(
    image,
    imgsz=1280,
    conf=0.15,
    iou=0.45,
    verbose=False
)

vehicle_classes = {
    2: "car",
    3: "motorcycle",
    5: "bus",
    7: "truck"
}

vehicle_count = 0

for result in results:

    if result.boxes is None:
        continue

    for box in result.boxes:

        class_id = int(box.cls[0].item())
        confidence = float(box.conf[0].item())

        class_name = model.names.get(
            class_id,
            str(class_id)
        )

        print(
            f"Detected: {class_name:<12} "
            f"confidence={confidence:.2f}"
        )

        if class_id in vehicle_classes:
            vehicle_count += 1

print("\n==========================================")
print(f"VEHICLES DETECTED: {vehicle_count}")
print("==========================================")