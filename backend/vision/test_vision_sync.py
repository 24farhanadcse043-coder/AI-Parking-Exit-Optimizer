import asyncio
import cv2

from services.vision_parking_sync import (
    VisionParkingSync
)


async def main():

    sync = VisionParkingSync(
        camera_source=0
    )

    try:

        sync.start_camera()

        print(
            "🅿️ Vision database synchronization test"
        )

        print(
            "Camera preview started."
        )

        print(
            "Press Q in the camera window to stop."
        )

        while True:

            frame = sync.read_frame()

            if frame is None:

                print(
                    "❌ Could not read camera frame."
                )

                break

            # Run YOLO parking detection
            parking_status = (
                sync.detector.analyze_frame(
                    frame
                )
            )

            # Update database
            sync.update_database(
                parking_status
            )

            # Calculate occupancy
            occupancy = (
                sync.get_occupancy_data(
                    parking_status
                )
            )

            # Draw parking spaces
            for space in parking_status:

                config = next(
                    item
                    for item in sync.detector.parking_spaces
                    if item["space_number"]
                    == space["space_number"]
                )

                x1 = config["x1"]
                y1 = config["y1"]
                x2 = config["x2"]
                y2 = config["y2"]

                if space["occupied"]:

                    box_color = (
                        0,
                        0,
                        255
                    )

                    status = "OCCUPIED"

                else:

                    box_color = (
                        0,
                        255,
                        0
                    )

                    status = "AVAILABLE"

                cv2.rectangle(
                    frame,
                    (x1, y1),
                    (x2, y2),
                    box_color,
                    2
                )

                cv2.putText(
                    frame,
                    (
                        f"{space['space_number']} "
                        f"{status}"
                    ),
                    (x1, y1 - 8),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.45,
                    box_color,
                    2
                )

            # Display occupancy information
            cv2.putText(
                frame,
                (
                    f"Occupied: "
                    f"{occupancy['occupied_spaces']}"
                ),
                (20, 35),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 255),
                2
            )

            cv2.putText(
                frame,
                (
                    f"Available: "
                    f"{occupancy['available_spaces']}"
                ),
                (20, 70),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 255),
                2
            )

            cv2.putText(
                frame,
                (
                    f"Occupancy: "
                    f"{occupancy['occupancy_percentage']:.1f}%"
                ),
                (20, 105),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 255),
                2
            )

            # Show camera
            cv2.imshow(
                "AI Parking - Vision Sync",
                frame
            )

            # Q = quit
            if cv2.waitKey(1) & 0xFF == ord("q"):

                break

            await asyncio.sleep(0.01)

    except KeyboardInterrupt:

        print(
            "\nStopping vision sync..."
        )

    finally:

        sync.stop()

        cv2.destroyAllWindows()


if __name__ == "__main__":

    asyncio.run(main())