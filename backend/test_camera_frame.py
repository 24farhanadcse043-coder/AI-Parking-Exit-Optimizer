import cv2

print("=" * 50)
print("   PARKAI — CAMERA FRAME TEST")
print("=" * 50)

print("\nOpening camera...")

camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("❌ Could not open camera.")
    exit()

print("✅ Camera opened.")

# Give the camera a moment to initialize
for _ in range(10):
    camera.read()

success, frame = camera.read()

if not success or frame is None:
    print("❌ Could not capture frame.")
    camera.release()
    exit()

height, width = frame.shape[:2]

print(f"\nCamera resolution: {width} x {height}")

output_file = "camera_test_frame.jpg"

cv2.imwrite(output_file, frame)

print(f"✅ Frame saved as: {output_file}")

camera.release()

print("\n==========================================")
print("CAMERA TEST FINISHED")
print("==========================================")