import cv2
import os

INPUT_IMAGE = "bus.jpg"
OUTPUT_VIDEO = "vehicle_test.mp4"

print("=" * 50)
print("   PARKAI — CREATE VEHICLE TEST VIDEO")
print("=" * 50)

if not os.path.exists(INPUT_IMAGE):
    print(f"❌ {INPUT_IMAGE} not found.")
    print("Run the YOLO image test first so bus.jpg exists.")
    exit()

image = cv2.imread(INPUT_IMAGE)

if image is None:
    print("❌ Could not load bus.jpg.")
    exit()

height, width = image.shape[:2]

print(f"\nImage size: {width} x {height}")

fourcc = cv2.VideoWriter_fourcc(*"mp4v")

video = cv2.VideoWriter(
    OUTPUT_VIDEO,
    fourcc,
    10.0,
    (width, height)
)

if not video.isOpened():
    print("❌ Could not create video.")
    exit()

# Create 100 frames = 10 seconds
for _ in range(100):
    video.write(image)

video.release()

print(f"✅ Vehicle test video created: {OUTPUT_VIDEO}")
print("✅ Duration: approximately 10 seconds")

print("\n==========================================")
print("VIDEO CREATION FINISHED")
print("==========================================")