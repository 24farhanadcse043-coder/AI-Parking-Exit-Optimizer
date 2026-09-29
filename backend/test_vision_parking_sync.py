import asyncio
import cv2

from services.vision_parking_sync import VisionParkingSync


IMAGE_PATH = "parking_test_frame.jpg"


class TestCamera:

    def read(self):
        frame = cv2.imread(IMAGE_PATH)

        if frame is None:
            raise RuntimeError(
                "Could not load parking_test_frame.jpg"
            )

        return frame


async def main():

    print("=" * 60)
    print("   PARKAI — VISION PARKING SYNC TEST")
    print("=" * 60)

    print("\nCreating test camera...")

    camera = TestCamera()

    print("✅ Test camera ready.")

    print("\nCreating VisionParkingSync...")

    sync = VisionParkingSync(
        camera=camera
    )

    print("✅ VisionParkingSync created.")

    print("\nProcessing parking test frame...")

    frame = camera.read()

    result = await sync.process_frame(
        frame
    )

    if result is None:

        print("❌ Vision processing returned no result.")

        return

    print("\n✅ Vision frame processed.")

    # -----------------------------------------------------
    # OCCUPANCY
    # -----------------------------------------------------

    occupancy = result["occupancy"]

    print("\nOccupancy result:")

    print(
        f"Total spaces: "
        f"{occupancy['total_spaces']}"
    )

    print(
        f"Occupied spaces: "
        f"{occupancy['occupied_spaces']}"
    )

    print(
        f"Available spaces: "
        f"{occupancy['available_spaces']}"
    )

    print(
        f"Occupancy percentage: "
        f"{occupancy['occupancy_percentage']}%"
    )

    # -----------------------------------------------------
    # TRACKING
    # -----------------------------------------------------

    tracking = result["vehicle_tracking"]

    print("\nVehicle tracking:")

    print(
        f"Active vehicles: "
        f"{tracking['active_vehicles']}"
    )

    print(
        f"Total entries: "
        f"{tracking['total_entries']}"
    )

    print(
        f"Total exits: "
        f"{tracking['total_exits']}"
    )

    # -----------------------------------------------------
    # DATABASE UPDATE
    # -----------------------------------------------------

    print("\nDatabase spaces updated:")

    print(
        f"Updated spaces: "
        f"{result['updated_spaces']}"
    )

    # -----------------------------------------------------
    # PARKING STATUS
    # -----------------------------------------------------

    print("\nParking status:")

    for status in result["parking_status"]:

        print(
            f"{status['space_number']}: "
            f"{'OCCUPIED' if status['occupied'] else 'FREE'} "
            f"| overlap={status['overlap']}"
        )

    # -----------------------------------------------------
    # FINAL CHECK
    # -----------------------------------------------------

    if (
        occupancy["occupied_spaces"] == 1
        and
        occupancy["available_spaces"] == 6
    ):

        print(
            "\n✅ VISION PARKING SYNCHRONIZATION "
            "IS WORKING."
        )

    else:

        print(
            "\n❌ VISION PARKING SYNCHRONIZATION "
            "RESULT IS NOT AS EXPECTED."
        )


if __name__ == "__main__":

    asyncio.run(main())