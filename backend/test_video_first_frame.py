import cv2
from ultralytics import YOLO

VIDEO_PATH = "vehicle_test.mp4"

print("=" * 50)
print("   PARKAI — VIDEO FRAME YOLO CHECK")
print("=" * 50)

# ---------------------------------------------------------
# OPEN VIDEO
# ---------------------------------------------------------

print("\nOpening video...")

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
    print("❌ Could not read first frame.")
    video.release()
    exit()

height, width = frame.shape[:2]

print("✅ First frame read.")
print(f"Frame size: {width} x {height}")

# Save extracted frame
output_image = "vehicle_video_first_frame.jpg"

cv2.imwrite(output_image, frame)

print(f"✅ Saved as: {output_image}")

video.release()

# ---------------------------------------------------------
# LOAD YOLO
# ---------------------------------------------------------

print("\nLoading YOLO model...")

model = YOLO("yolo11n.pt")

print("✅ YOLO model loaded.")

# ---------------------------------------------------------
# RUN YOLO
# ---------------------------------------------------------

print("\nRunning YOLO on extracted video frame...")

results = model(
    frame,
    imgsz=1280,
    conf=0.05,
    iou=0.45,
    verbose=False
)

# YOLO COCO vehicle classes
vehicle_classes = {
    2: "car",
    3: "motorcycle",
    5: "bus",
    7: "truck"
}

vehicle_count = 0

print("\nDetected objects:")

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

# ---------------------------------------------------------
# RESULT
# ---------------------------------------------------------

print("\n==========================================")
print(f"VEHICLES DETECTED: {vehicle_count}")
print("==========================================")

if vehicle_count > 0:

    print("✅ Vehicle detected in the video frame.")

else:

    print("❌ No vehicle detected in the video frame.")

print("\nThe extracted frame is saved as:")

print(output_image)

print("\nOpen it with:")

print(f"open {output_image}")