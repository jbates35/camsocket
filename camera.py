from picamera import PiCamera
from time import sleep
import numpy as np
from threading import Thread, Lock

class Camera(Thread):
    """
    Simple class to capture the raw pi camera
    
    Inspired by: https://picamera.readthedocs.io/en/release-1.13/recipes2.html#:~:text=4.1.-,Capturing%20to%20a%20numpy%20array,written%20directly%20to%20the%20object.
    
    Attributes
    -----
    none

    Methods
    ----
    run()
        Captures image and loads it into array
    """
    def __init__(self, camsize = (320,240), framerate=8):
        Thread.__init__(self)
        
        #Store framerate
        self.camsize = camsize
        self.width = camsize[0]
        self.height = camsize[1]
        self.framerate = framerate
        
        #Main camera object, set camera to 320x240 by default
        self.camera = PiCamera()
        self.camera.resolution = (self.camsize)
        self.camera.framerate = framerate
        
        #mutex for image
        self.mutex = Lock()
        
        #exit flag to leave run thread
        self.exit = False
        
        #initialize empty array for storing image later
        self.image = np.empty((self.height * self.width * 3,), dtype=np.uint8)
        sleep(0.2)
        

    def run(self):
        """
        Returns an object holding the bgr array from the pi camera
        Send this into cv stream
        """
        while self.exit==False:
            #protect image from being corrupted
            self.mutex.acquire()
            
            #capture camera and refresh self.image to hold array of values
            try:
                self.camera.capture(self.image,'bgr')
                self.image = self.image.reshape((self.height, self.width, 3))
            
            #release mutex
            finally:
                self.mutex.release()
            
            sleep(1.0/self.framerate)
