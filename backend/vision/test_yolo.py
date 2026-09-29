from ultralytics import YOLO

print("Loading YOLO model...")

model = YOLO("yolo11n.pt")

print("✅ YOLO model loaded successfully!")

print("\nModel classes:")

for class_id, class_name in model.names.items():
    print(class_id, "=", class_name)