from vision.vehicle_tracker import VehicleTracker


tracker = VehicleTracker()


# Simulated first camera frame
vehicles_frame_1 = [
    {
        "type": "car",
        "confidence": 0.90,
        "x": 100,
        "y": 100,
        "width": 100,
        "height": 80
    }
]


result_1 = tracker.update(
    vehicles_frame_1
)

print("Frame 1:")
print(result_1)

print(
    "Active vehicles:",
    tracker.get_active_vehicles()
)


# Simulated second camera frame
# Same vehicle moved slightly
vehicles_frame_2 = [
    {
        "type": "car",
        "confidence": 0.92,
        "x": 110,
        "y": 105,
        "width": 100,
        "height": 80
    }
]


result_2 = tracker.update(
    vehicles_frame_2
)

print()
print("Frame 2:")
print(result_2)

print(
    "Active vehicles:",
    tracker.get_active_vehicles()
)


# Basic verification

if result_1["total_entries"] != 1:

    raise RuntimeError(
        "❌ Vehicle entry tracking failed."
    )


if result_2["active_vehicles"] != 1:

    raise RuntimeError(
        "❌ Same vehicle was not tracked."
    )


if result_2["total_entries"] != 1:

    raise RuntimeError(
        "❌ Tracker created a duplicate vehicle."
    )


print()
print(
    "✅ Vehicle tracking test passed."
)