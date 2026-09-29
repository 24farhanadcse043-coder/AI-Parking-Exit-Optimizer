import cv2


class CameraManager:

    def __init__(self):

        self.camera = None

    # -----------------------------------------------------
    # Open camera
    # -----------------------------------------------------

    def open_camera(self, camera_source=0):

        self.camera = cv2.VideoCapture(
            camera_source
        )

        if not self.camera.isOpened():

            raise RuntimeError(
                "Unable to open camera"
            )

        return True

    # -----------------------------------------------------
    # Read frame
    # -----------------------------------------------------

    def read_frame(self):

        if self.camera is None:
            return None

        success, frame = self.camera.read()

        if not success:
            return None

        return frame

    # -----------------------------------------------------
    # Release camera
    # -----------------------------------------------------

    def release_camera(self):

        if self.camera is not None:

            self.camera.release()

            self.camera = None