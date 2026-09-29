import cv2
import numpy as np

INPUT_IMAGE = "bus.jpg"
OUTPUT_IMAGE = "parking_test_frame.jpg"

FRAME_WIDTH = 1280
FRAME_HEIGHT = 720

print("=" * 60)
print("   PARKAI — CLEAN PARKING TEST FRAME")
print("=" * 60)

print("\nLoading bus image...")

bus = cv2.imread(INPUT_IMAGE)

if bus is None:
    print("❌ Could not load bus.jpg")
    exit()

print("✅ bus.jpg loaded.")

# ---------------------------------------------------------
# CREATE CLEAN 1280 x 720 BACKGROUND
# ---------------------------------------------------------

frame = np.zeros(
    (FRAME_HEIGHT, FRAME_WIDTH, 3),
    dtype=np.uint8
)

# Use a neutral background
frame[:] = (60, 60, 60)

# ---------------------------------------------------------
# RESIZE BUS
# ---------------------------------------------------------

target_width = 300
target_height = 300

bus = cv2.resize(
    bus,
    (target_width, target_height)
)

# ---------------------------------------------------------
# PLACE BUS INSIDE P001
# ---------------------------------------------------------

x = 150
y = 210

frame[
    y:y + target_height,
    x:x + target_width
] = bus

# ---------------------------------------------------------
# DRAW P001
# ---------------------------------------------------------

cv2.rectangle(
    frame,
    (77, 179),
    (631, 537),
    (0, 255, 0),
    3
)

cv2.putText(
    frame,
    "P001",
    (90, 165),
    cv2.FONT_HERSHEY_SIMPLEX,
    1.0,
    (0, 255, 0),
    2
)

# ---------------------------------------------------------
# DRAW OTHER PARKING AREAS
# ---------------------------------------------------------

parking_spaces = {
    "P002": (716, 142, 855, 371),
    "P003": (1062, 145, 1241, 323),
    "P004": (664, 459, 913, 585),
    "P005": (934, 432, 1029, 490),
    "P006": (540, 432, 934, 684),
    "P007": (886, 202, 1105, 497),
}

for name, coordinates in parking_spaces.items():

    x1, y1, x2, y2 = coordinates

    cv2.rectangle(
        frame,
        (x1, y1),
        (x2, y2),
        (100, 100, 100),
        2
    )

    cv2.putText(
        frame,
        name,
        (x1 + 5, y1 - 5),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (180, 180, 180),
        1
    )

# ---------------------------------------------------------
# SAVE
# ---------------------------------------------------------

success = cv2.imwrite(
    OUTPUT_IMAGE,
    frame
)

if not success:
    print("❌ Could not save test frame.")
    exit()

print(
    f"✅ Clean test frame saved as: "
    f"{OUTPUT_IMAGE}"
)

print(
    f"Frame size: "
    f"{FRAME_WIDTH} x {FRAME_HEIGHT}"
)

print(
    "\n✅ One bus is placed inside P001."
)

print(
    "✅ Background contains no other vehicle."
)

print("\n==========================================")
print("CLEAN PARKING TEST FRAME CREATED")
print("==========================================")