from picamera.array import PiRGBArray
from picamera import PiCamera
import time

class Camera:
    """
    Simple class to capture the raw pi camera
    
    Attributes
    -----
    none

    Methods
    ----
    capture()
        Use capture to load a new image into an array
    """
    def __init__(self):
        #Open camera feed and declare array to capture object
        self.camera = PiCamera()
        self.rawCapture = PiRGBArray(self.camera)
        time.sleep(0.1)

        #Settings for camera
        self.camera.capture(self.rawCapture,format="bgr")

    def capture(self):
        """
        Returns an object holding the bgr array from the pi camera
        Send this into cv stream
        """
        return self.rawCapture.array
