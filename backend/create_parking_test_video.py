import cv2

IMAGE_PATH = "parking_test_frame.jpg"
OUTPUT_VIDEO = "parking_test_video.mp4"

FPS = 5
FRAME_COUNT = 50

print("=" * 60)
print("   PARKAI — CREATE 1280x720 PARKING TEST VIDEO")
print("=" * 60)

frame = cv2.imread(IMAGE_PATH)

if frame is None:
    print("❌ Could not load parking_test_frame.jpg")
    exit()

height, width = frame.shape[:2]

print(f"Input frame: {width} x {height}")

if width != 1280 or height != 720:
    print("❌ The test frame is not 1280 x 720.")
    exit()

fourcc = cv2.VideoWriter_fourcc(
    *"mp4v"
)

video = cv2.VideoWriter(
    OUTPUT_VIDEO,
    fourcc,
    FPS,
    (1280, 720)
)

if not video.isOpened():
    print("❌ Could not create output video.")
    exit()

for _ in range(FRAME_COUNT):
    video.write(frame)

video.release()

print(
    f"✅ Created: {OUTPUT_VIDEO}"
)

print(
    "✅ Resolution: 1280 x 720"
)

print(
    f"✅ Frames: {FRAME_COUNT}"
)

print(
    f"✅ Duration: {FRAME_COUNT / FPS:.1f} seconds"
)

print("\n==========================================")
print("TEST VIDEO CREATION FINISHED")
print("==========================================")