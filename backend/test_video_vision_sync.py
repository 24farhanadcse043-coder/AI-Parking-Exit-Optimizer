import asyncio
import cv2

from services.vision_parking_sync import VisionParkingSync


VIDEO_PATH = "parking_test_video.mp4"


class VideoTestCamera:

    def __init__(self, video_path):

        self.video = cv2.VideoCapture(
            video_path
        )

        if not self.video.isOpened():

            raise RuntimeError(
                f"Could not open {video_path}"
            )

    def read(self):

        success, frame = (
            self.video.read()
        )

        if not success:

            self.video.set(
                cv2.CAP_PROP_POS_FRAMES,
                0
            )

            success, frame = (
                self.video.read()
            )

        if not success:

            return None

        return frame

    def release(self):

        self.video.release()


async def main():

    print("=" * 60)
    print("   PARKAI — 1280x720 FULL VISION SYNC TEST")
    print("=" * 60)

    print("\nOpening test video...")

    camera = VideoTestCamera(
        VIDEO_PATH
    )

    print("✅ Test video opened.")

    print("\nCreating VisionParkingSync...")

    sync = VisionParkingSync(
        camera=camera
    )

    print("✅ VisionParkingSync created.")

    print("\nProcessing 10 video frames...")

    for frame_number in range(1, 11):

        frame = camera.read()

        if frame is None:

            print(
                f"Frame {frame_number}: "
                "no frame."
            )

            continue

        result = await sync.process_frame(
            frame
        )

        occupancy = result["occupancy"]

        tracking = result["vehicle_tracking"]

        occupied = [
            status["space_number"]
            for status
            in result["parking_status"]
            if status["occupied"]
        ]

        print(
            f"\nFrame {frame_number:02d}"
        )

        print(
            f"Occupied spaces: {occupied}"
        )

        print(
            f"Occupied count: "
            f"{occupancy['occupied_spaces']}"
        )

        print(
            f"Available count: "
            f"{occupancy['available_spaces']}"
        )

        print(
            f"Active vehicles: "
            f"{tracking['active_vehicles']}"
        )

    camera.release()

    print("\n" + "=" * 60)
    print("FULL VISION SYNC TEST FINISHED")
    print("=" * 60)

    print(
        "\nExpected:"
    )

    print(
        "P001 occupied, "
        "P002-P007 free, "
        "1 active vehicle."
    )


if __name__ == "__main__":

    asyncio.run(main())