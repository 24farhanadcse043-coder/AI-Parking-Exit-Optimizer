import cv2
import numpy as np
import requests
from ultralytics import YOLO


STREAM_URL = "http://127.0.0.1:8000/api/vision/camera/stream"
MODEL_PATH = "yolo11n.pt"


print("==========================================")
print("      PARKAI — LIVE YOLO TEST")
print("==========================================")

print("\nLoading YOLO model...")

model = YOLO(MODEL_PATH)

print("✅ YOLO model loaded.")
print("Connecting to live camera stream...")
print(STREAM_URL)


VEHICLE_CLASSES = {
    2: "car",
    3: "motorcycle",
    5: "bus",
    7: "truck"
}


try:

    response = requests.get(
        STREAM_URL,
        stream=True,
        timeout=10
    )

    response.raise_for_status()

    print("✅ Camera stream connected.")

    buffer = b""

    frame_count = 0

    while True:

        chunk = response.raw.read(
            8192
        )

        if not chunk:
            print("❌ Camera stream ended.")
            break

        buffer += chunk

        start = buffer.find(
            b"\xff\xd8"
        )

        end = buffer.find(
            b"\xff\xd9"
        )

        if (
            start == -1
            or end == -1
            or end <= start
        ):
            continue

        jpg_data = buffer[
            start:end + 2
        ]

        buffer = buffer[
            end + 2:
        ]

        frame = cv2.imdecode(
            np.frombuffer(
                jpg_data,
                dtype=np.uint8
            ),
            cv2.IMREAD_COLOR
        )

        if frame is None:
            continue

        frame_count += 1

        print(
            f"\nFrame {frame_count}"
        )

        results = model(
            frame,
            imgsz=1280,
            conf=0.15,
            iou=0.45,
            verbose=False
        )

        detected_vehicles = []

        for result in results:

            if result.boxes is None:
                continue

            for box in result.boxes:

                class_id = int(
                    box.cls[0].item()
                )

                confidence = float(
                    box.conf[0].item()
                )

                class_name = model.names[
                    class_id
                ]

                print(
                    f"Detected: "
                    f"{class_name} "
                    f"confidence={confidence:.2f}"
                )

                if class_id in VEHICLE_CLASSES:

                    detected_vehicles.append(
                        {
                            "type": VEHICLE_CLASSES[
                                class_id
                            ],
                            "confidence": round(
                                confidence,
                                2
                            )
                        }
                    )

        if detected_vehicles:

            print(
                "\n✅ VEHICLES DETECTED:"
            )

            for vehicle in detected_vehicles:

                print(
                    f"   {vehicle['type']} "
                    f"({vehicle['confidence']})"
                )

        else:

            print(
                "⚠️ No vehicles detected."
            )

        if frame_count >= 20:

            print(
                "\n=========================================="
            )
            print(
                "YOLO TEST FINISHED"
            )
            print(
                "=========================================="
            )

            break


except requests.exceptions.RequestException as error:

    print(
        "\n❌ Unable to connect to camera stream:"
    )

    print(error)


except KeyboardInterrupt:

    print(
        "\nTest stopped."
    )


except Exception as error:

    print(
        "\n❌ YOLO test error:"
    )

    print(error)