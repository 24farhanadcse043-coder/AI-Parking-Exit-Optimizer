import asyncio

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from services.vision_state import (
    vision_sync,
    vision_manager
)

from services.shared_camera import shared_camera


router = APIRouter(
    prefix="/api/vision",
    tags=["Computer Vision"]
)


# =========================================================
# VISION STATUS
# =========================================================

@router.get("/status")
def get_vision_status():

    return {
        "status": "ACTIVE",

        "vision_ai": {
            "running": vision_manager.running,
            "latest_analysis":
                vision_manager.get_latest_result()
        },

        "parking_vision": {
            "occupancy":
                vision_sync.get_latest_occupancy(),

            "vehicle_tracking":
                vision_sync.get_latest_tracking()
        }
    }


# =========================================================
# CAMERA STATUS
# =========================================================

@router.get("/camera/status")
def get_camera_status():

    return {
        "camera": "ONLINE"
        if shared_camera.is_running()
        else "OFFLINE",

        "running":
            shared_camera.is_running(),

        "frame_available":
            shared_camera.get_latest_frame()
            is not None
    }


# =========================================================
# LIVE CAMERA FRAME
# =========================================================

def generate_camera_stream():

    while shared_camera.is_running():

        frame = (
            shared_camera.get_latest_frame()
        )

        if frame is None:

            asyncio.run(
                asyncio.sleep(0.1)
            )

            continue

        success, encoded_frame = (
            __import__("cv2").imencode(
                ".jpg",
                frame
            )
        )

        if not success:

            continue

        frame_bytes = (
            encoded_frame.tobytes()
        )

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n"
            + frame_bytes
            + b"\r\n"
        )

        asyncio.run(
            asyncio.sleep(0.05)
        )


# =========================================================
# CAMERA STREAM ENDPOINT
# =========================================================

@router.get("/camera/stream")
def camera_stream():

    return StreamingResponse(
        generate_camera_stream(),
        media_type=(
            "multipart/x-mixed-replace;"
            " boundary=frame"
        )
    )