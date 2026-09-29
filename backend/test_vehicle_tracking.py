import cv2

from vision.vehicle_detection import VehicleDetector
from vision.vehicle_tracker import VehicleTracker


VIDEO_PATH = "vehicle_test.mp4"


print("=" * 55)
print("   PARKAI — VEHICLE DETECTION + TRACKING TEST")
print("=" * 55)


# ---------------------------------------------------------
# LOAD VEHICLE DETECTOR
# ---------------------------------------------------------

print("\nLoading VehicleDetector...")

detector = VehicleDetector()

print("✅ VehicleDetector loaded.")


# ---------------------------------------------------------
# LOAD VEHICLE TRACKER
# ---------------------------------------------------------

print("\nLoading VehicleTracker...")

tracker = VehicleTracker()

print("✅ VehicleTracker loaded.")


# ---------------------------------------------------------
# OPEN VIDEO
# ---------------------------------------------------------

print("\nOpening vehicle test video...")

video = cv2.VideoCapture(VIDEO_PATH)

if not video.isOpened():

    print("❌ Could not open vehicle_test.mp4")

    exit()

print("✅ Video opened.")


# ---------------------------------------------------------
# PROCESS VIDEO
# ---------------------------------------------------------

MAX_FRAMES = 20

frame_number = 0


while frame_number < MAX_FRAMES:

    success, frame = video.read()

    if not success:

        print("\n⚠️ Video ended.")

        break

    frame_number += 1


    # -----------------------------------------------------
    # DETECT VEHICLES
    # -----------------------------------------------------

    detected_vehicles = detector.detect_vehicles(frame)


    # -----------------------------------------------------
    # UPDATE TRACKER
    # -----------------------------------------------------

    statistics = tracker.update(
        detected_vehicles
    )


    # -----------------------------------------------------
    # DISPLAY RESULT
    # -----------------------------------------------------

    print(
        f"\nFrame {frame_number:02d}"
    )

    print(
        f"Detected vehicles: "
        f"{len(detected_vehicles)}"
    )


    active_vehicles = tracker.get_active_vehicles()


    for vehicle in active_vehicles:

        print(
            f"  ID={vehicle['vehicle_id']} "
            f"type={vehicle['type']} "
            f"center=("
            f"{vehicle['center_x']:.1f}, "
            f"{vehicle['center_y']:.1f}"
            f") "
            f"status={vehicle['status']}"
        )


    print(
        f"Active vehicles: "
        f"{statistics['active_vehicles']}"
    )

    print(
        f"Total entries: "
        f"{statistics['total_entries']}"
    )

    print(
        f"Total exits: "
        f"{statistics['total_exits']}"
    )


# ---------------------------------------------------------
# CLEANUP
# ---------------------------------------------------------

video.release()


# ---------------------------------------------------------
# FINAL RESULT
# ---------------------------------------------------------

print("\n" + "=" * 55)
print("VEHICLE TRACKING TEST FINISHED")
print("=" * 55)

final_statistics = tracker.get_statistics()

print(
    f"Frames processed: "
    f"{frame_number}"
)

print(
    f"Active vehicles: "
    f"{final_statistics['active_vehicles']}"
)

print(
    f"Total entries: "
    f"{final_statistics['total_entries']}"
)

print(
    f"Total exits: "
    f"{final_statistics['total_exits']}"
)

print(
    "\nFinal tracked vehicles:"
)

for vehicle in tracker.get_active_vehicles():

    print(
        f"  {vehicle['vehicle_id']} "
        f"-> {vehicle['type']} "
        f"-> {vehicle['status']}"
    )


if final_statistics["total_entries"] == 1:

    print(
        "\n✅ ONE VEHICLE WAS TRACKED "
        "ACROSS THE VIDEO."
    )

elif final_statistics["total_entries"] > 1:

    print(
        "\n⚠️ MULTIPLE VEHICLE IDs WERE CREATED."
    )

else:

    print(
        "\n❌ NO VEHICLE WAS TRACKED."
    )