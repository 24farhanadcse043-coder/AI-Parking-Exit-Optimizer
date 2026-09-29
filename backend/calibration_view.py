import cv2
import json
import os


# =========================================================
# SETTINGS
# =========================================================

CAMERA_SOURCE = 0

LAYOUT_FILE = "parking_layout.json"

OUTPUT_FILE = "parking_calibration.jpg"


# =========================================================
# LOAD PARKING LAYOUT
# =========================================================

with open(
    LAYOUT_FILE,
    "r",
    encoding="utf-8"
) as file:

    parking_spaces = json.load(file)


# =========================================================
# OPEN CAMERA
# =========================================================

camera = cv2.VideoCapture(
    CAMERA_SOURCE
)

if not camera.isOpened():

    print(
        "❌ Unable to open camera."
    )

    raise SystemExit


print(
    "✅ Camera opened."
)


# =========================================================
# READ FRAME
# =========================================================

success, frame = camera.read()

if not success:

    print(
        "❌ Unable to capture frame."
    )

    camera.release()

    raise SystemExit


# =========================================================
# DRAW PARKING REGIONS
# =========================================================

for space in parking_spaces:

    x1 = int(
        space["x1"]
    )

    y1 = int(
        space["y1"]
    )

    x2 = int(
        space["x2"]
    )

    y2 = int(
        space["y2"]
    )

    name = space[
        "space_number"
    ]


    # -----------------------------------------------------
    # Draw rectangle
    # -----------------------------------------------------

    cv2.rectangle(
        frame,
        (x1, y1),
        (x2, y2),
        (0, 255, 0),
        3
    )


    # -----------------------------------------------------
    # Label background
    # -----------------------------------------------------

    label_width = 110
    label_height = 35

    cv2.rectangle(
        frame,
        (
            x1,
            max(
                0,
                y1 - label_height
            )
        ),
        (
            x1 + label_width,
            y1
        ),
        (0, 0, 0),
        -1
    )


    # -----------------------------------------------------
    # Label
    # -----------------------------------------------------

    cv2.putText(
        frame,
        name,
        (
            x1 + 5,
            max(
                22,
                y1 - 8
            )
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 255),
        2,
        cv2.LINE_AA
    )


# =========================================================
# SAVE IMAGE
# =========================================================

saved = cv2.imwrite(
    OUTPUT_FILE,
    frame
)

camera.release()


if not saved:

    print(
        "❌ Unable to save calibration image."
    )

    raise SystemExit


# =========================================================
# ABSOLUTE PATH
# =========================================================

absolute_path = os.path.abspath(
    OUTPUT_FILE
)


print()
print(
    "✅ Calibration image created."
)

print(
    f"📷 File: {absolute_path}"
)

print()
print(
    "Open this image and check P001-P007."
)