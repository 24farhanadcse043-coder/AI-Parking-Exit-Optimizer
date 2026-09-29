from ultralytics import YOLO


class VehicleDetector:

    def __init__(self):

        print("Loading YOLO vehicle detector...")

        self.model = YOLO("yolo11n.pt")

        self.vehicle_classes = {
            2: "car",
            3: "motorcycle",
            5: "bus",
            7: "truck"
        }

        print("✅ YOLO vehicle detector ready.")

    def detect_vehicles(self, frame):

        if frame is None:
            return []

        results = self.model(
            frame,
            imgsz=1280,
            conf=0.05,
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

                if class_id not in self.vehicle_classes:
                    continue

                confidence = float(
                    box.conf[0].item()
                )

                x1, y1, x2, y2 = (
                    box.xyxy[0].tolist()
                )

                width = int(x2 - x1)
                height = int(y2 - y1)

                if width <= 0 or height <= 0:
                    continue

                detected_vehicles.append({
                    "type": self.vehicle_classes[class_id],
                    "confidence": round(
                        confidence,
                        2
                    ),
                    "x": int(x1),
                    "y": int(y1),
                    "width": width,
                    "height": height
                })

        return detected_vehicles

    def get_vehicle_counts(self, vehicles):

        counts = {
            "car": 0,
            "motorcycle": 0,
            "bus": 0,
            "truck": 0
        }

        for vehicle in vehicles:

            vehicle_type = vehicle["type"]

            if vehicle_type in counts:

                counts[vehicle_type] += 1

        counts["total"] = len(vehicles)

        return counts


def count_vehicles(frame):

    detector = VehicleDetector()

    vehicles = detector.detect_vehicles(frame)

    return len(vehicles)