import cv2
import json

from vision.camera_manager import CameraManager


OUTPUT_FILE = "exit_regions.json"

regions = {}


def select_region(camera, exit_name):

    print()
    print(f"🅿️ Calibrating {exit_name}")
    print("Click TOP-LEFT corner.")
    print("Then click BOTTOM-RIGHT corner.")
    print("Press Q to cancel.")
    print()

    points = []

    window_name = f"Calibrating {exit_name}"

    cv2.namedWindow(window_name)

    def mouse_callback(event, x, y, flags, param):

        if event == cv2.EVENT_LBUTTONDOWN:

            points.append((x, y))

            print(
                f"📍 Point {len(points)}: ({x}, {y})"
            )

    cv2.setMouseCallback(
        window_name,
        mouse_callback
    )

    while True:

        frame = camera.read_frame()

        if frame is None:

            print("❌ Camera frame unavailable.")

            cv2.destroyWindow(window_name)

            return None

        display = frame.copy()

        for point in points:

            cv2.circle(
                display,
                point,
                6,
                (0, 0, 255),
                -1
            )

        if len(points) == 2:

            x1 = min(
                points[0][0],
                points[1][0]
            )

            y1 = min(
                points[0][1],
                points[1][1]
            )

            x2 = max(
                points[0][0],
                points[1][0]
            )

            y2 = max(
                points[0][1],
                points[1][1]
            )

            cv2.rectangle(
                display,
                (x1, y1),
                (x2, y2),
                (0, 255, 0),
                2
            )

            cv2.putText(
                display,
                exit_name,
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2
            )

        cv2.imshow(
            window_name,
            display
        )

        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):

            cv2.destroyWindow(window_name)

            return None

        if len(points) == 2:

            x1 = min(
                points[0][0],
                points[1][0]
            )

            y1 = min(
                points[0][1],
                points[1][1]
            )

            x2 = max(
                points[0][0],
                points[1][0]
            )

            y2 = max(
                points[0][1],
                points[1][1]
            )

            cv2.destroyWindow(window_name)

            return {
                "x1": x1,
                "y1": y1,
                "x2": x2,
                "y2": y2
            }


def main():

    camera = CameraManager()

    try:

        camera.open_camera(0)

        print()
        print("======================================")
        print(" EXIT REGION CALIBRATION")
        print("======================================")
        print()
        print("You will configure:")
        print("1. Exit A")
        print("2. Exit B")
        print("3. Exit C")
        print()

        for exit_name in [
            "Exit A",
            "Exit B",
            "Exit C"
        ]:

            input(
                f"Press ENTER to configure {exit_name}..."
            )

            region = select_region(
                camera,
                exit_name
            )

            if region is None:

                print(
                    f"❌ {exit_name} calibration cancelled."
                )

                return

            regions[exit_name] = region

            print(
                f"✅ {exit_name} saved:"
            )

            print(region)

        with open(
            OUTPUT_FILE,
            "w"
        ) as file:

            json.dump(
                regions,
                file,
                indent=4
            )

        print()
        print(
            "======================================"
        )

        print(
            "✅ Exit regions saved successfully!"
        )

        print(
            f"📄 File: {OUTPUT_FILE}"
        )

        print(
            "======================================"
        )

        print()

    finally:

        camera.release_camera()

        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()