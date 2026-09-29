from services.shared_camera import shared_camera

from services.vision_parking_sync import VisionParkingSync
from services.vision_manager import VisionManager


vision_sync = VisionParkingSync(
    camera=shared_camera
)

vision_manager = VisionManager(
    camera=shared_camera
)