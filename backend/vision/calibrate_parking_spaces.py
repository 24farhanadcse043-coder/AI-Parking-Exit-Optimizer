import cv2
import json


WINDOW_NAME = "Parking Space Calibration"

points = []
parking_spaces = []


def mouse_callback(event, x, y, flags, param):
    global points

    if event == cv2.EVENT_LBUTTONDOWN:

        points.append((x, y))

        print(f"Point selected: ({x}, {y})")

        if len(points) == 2:

            x1, y1 = points[0]
            x2, y2 = points[1]

            left = min(x1, x2)
            right = max(x1, x2)

            top = min(y1, y2)
            bottom = max(y1, y2)

            width = right - left
            height = bottom - top

            # Reject extremely small regions
            if width < 20 or height < 20:
                print()
                print("⚠️ Parking space is too small.")
                print("Please select a larger region.")
                points = []
                return

            space_number = (
                f"P{len(parking_spaces) + 1:03d}"
            )

            parking_spaces.append({
                "space_number": space_number,
                "x1": left,
                "y1": top,
                "x2": right,
                "y2": bottom
            })

            print()
            print(
                f"✅ {space_number} created: "
                f"({left}, {top}) -> "
                f"({right}, {bottom})"
            )

            print(
                f"Total spaces selected: "
                f"{len(parking_spaces)}"
            )

            print()

            points = []


def save_spaces():

    with open(
        "parking_layout.json",
        "w"
    ) as file:

        json.dump(
            parking_spaces,
            file,
            indent=4
        )

    print()
    print("================================")
    print(
        f"✅ Saved {len(parking_spaces)} "
        "parking spaces."
    )
    print("📄 File: parking_layout.json")
    print("================================")
    print()


def main():

    camera = cv2.VideoCapture(0)

    if not camera.isOpened():

        print(
            "❌ Could not open camera."
        )

        return

    cv2.namedWindow(WINDOW_NAME)

    cv2.setMouseCallback(
        WINDOW_NAME,
        mouse_callback
    )

    print()
    print("🅿️ PARKING SPACE CALIBRATION")
    print("================================")
    print()
    print(
        "Click TWO points for each parking space."
    )
    print(
        "First point = one corner"
    )
    print(
        "Second point = opposite corner"
    )
    print()
    print("Keyboard controls:")
    print("S = Save")
    print("R = Reset")
    print("Q = Quit")
    print()
    print("⚠️ Select ONE parking space at a time.")
    print("================================")
    print()

    while True:

        success, frame = camera.read()

        if not success:

            print(
                "❌ Could not read camera."
            )

            break

        display = frame.copy()

        # Draw existing parking spaces
        for space in parking_spaces:

            x1 = space["x1"]
            y1 = space["y1"]
            x2 = space["x2"]
            y2 = space["y2"]

            cv2.rectangle(
                display,
                (x1, y1),
                (x2, y2),
                (0, 255, 0),
                2
            )

            cv2.putText(
                display,
                space["space_number"],
                (x1, max(y1 - 8, 20)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )

        # Draw currently selected points
        for point in points:

            cv2.circle(
                display,
                point,
                6,
                (0, 0, 255),
                -1
            )

        # Show number of spaces
        cv2.putText(
            display,
            f"Spaces: {len(parking_spaces)}",
            (20, 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2
        )

        cv2.putText(
            display,
            "S=Save  R=Reset  Q=Quit",
            (20, 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2
        )

        cv2.imshow(
            WINDOW_NAME,
            display
        )

        key = cv2.waitKey(1) & 0xFF

        # SAVE
        if key == ord("s"):

            if len(parking_spaces) == 0:

                print()
                print(
                    "⚠️ No parking spaces selected."
                )
                print(
                    "Select at least one space."
                )

            else:

                save_spaces()

                print(
                    "Press Q to close the "
                    "calibration window."
                )

        # RESET
        elif key == ord("r"):

            parking_spaces.clear()
            points.clear()

            print()
            print(
                "🔄 All parking spaces reset."
            )
            print()

        # QUIT
        elif key == ord("q"):

            print()
            print("👋 Calibration closed.")
            break

    camera.release()

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()