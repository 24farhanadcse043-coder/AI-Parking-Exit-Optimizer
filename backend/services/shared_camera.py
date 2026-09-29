import cv2
import threading


class SharedCamera:

    def __init__(
        self,
        camera_source=0,
        loop_video=False
    ):

        self.camera_source = camera_source

        self.loop_video = loop_video

        self.camera = None

        self.running = False

        self.latest_frame = None

        self.lock = threading.Lock()

    # =====================================================
    # START CAMERA / VIDEO
    # =====================================================

    def start(self):

        if self.camera is not None:
            return True

        self.camera = cv2.VideoCapture(
            self.camera_source
        )

        if not self.camera.isOpened():

            self.camera = None

            raise RuntimeError(
                "Unable to open shared camera/video."
            )

        self.running = True

        print(
            f"🎥 Shared camera started: "
            f"{self.camera_source}"
        )

        return True

    # =====================================================
    # READ FRAME
    # =====================================================

    def read(self):

        if self.camera is None:
            return None

        success, frame = self.camera.read()

        # -------------------------------------------------
        # VIDEO FILE REACHED END
        # -------------------------------------------------

        if not success:

            if (
                self.loop_video
                and
                isinstance(
                    self.camera_source,
                    str
                )
            ):

                self.camera.set(
                    cv2.CAP_PROP_POS_FRAMES,
                    0
                )

                success, frame = (
                    self.camera.read()
                )

            else:

                return None

        if not success or frame is None:
            return None

        with self.lock:

            self.latest_frame = (
                frame.copy()
            )

        return frame

    # =====================================================
    # GET LATEST FRAME
    # =====================================================

    def get_latest_frame(self):

        with self.lock:

            if self.latest_frame is None:
                return None

            return self.latest_frame.copy()

    # =====================================================
    # CAMERA STATUS
    # =====================================================

    def is_running(self):

        return (
            self.running
            and
            self.camera is not None
        )

    # =====================================================
    # STOP
    # =====================================================

    def stop(self):

        self.running = False

        if self.camera is not None:

            self.camera.release()

            self.camera = None

        with self.lock:

            self.latest_frame = None

        print(
            "🎥 Shared camera stopped."
        )

# =========================================================
# DEFAULT VIDEO TEST SOURCE
# =========================================================

shared_camera = SharedCamera(
    camera_source=0,
    loop_video=False
)