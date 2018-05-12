"""
A client for getting images from a Raspberry Pi camera.
"""

import multiprocessing
import cv2
import numpy as np
import picamera
from picamera.array import PiRGBArray

class Camera(multiprocessing.Process):
    """
    Implements a task for fetching camera images from a Raspberry Pi camera.
    """

    def __init__(self, output_queue,
                 resolution=(1024,768),
                 framerate=32,
                 roi_horizontal=None,
                 roi_vertical=None):
        """
        Constructor for the Camera class.

        :param output_queue: multiprocessing.Queue containing output data
        """

        # Initialize multiprocessing.Process parent
        multiprocessing.Process.__init__(self)

        # Establish queue
        self._output_queue = output_queue

        # Exit event for stopping the process
        self._exit = multiprocessing.Event()

        # Initialize variables
        self._resolution = resolution
        self._framerate = framerate
        self._roi_horizontal = roi_horizontal
        self._roi_vertical = roi_vertical


    def run(self):
        """
        Function called when task is started (e.g. task.start()). Overrides run function of multiprocessing. Process
        parent
        """

        # Clear exit event just to be sure
        self._exit.clear()

        # Setup the camera
        camera = picamera.PiCamera()
        camera.resolution = self._resolution
        camera.framerate = self._framerate
        rawCapture = PiRGBArray(camera, size=self._resolution)


        # While exit event is not set...
        while not self._exit.is_set():
            camera.capture(rawCapture, format='rgb')
            buf = rawCapture.array
            rawCapture.truncate(0)
            img = cv2.cvtColor(buf, cv2.COLOR_RGB2GRAY)

            # ...apply ROIs if specified
            if self._roi_vertical:
                img = img[self._roi_vertical[0]:self._roi_vertical[1],
                          :]

            if self._roi_horizontal:
                img = img[:,
                          self._roi_horizontal[0]:self._roi_horizontal[1]]

            # ...put image into output queue
            data = ({'camera_image': img})
            self._output_queue.put(data)

        # If exit event set...
        if self._exit.is_set():
            # ...shutdown
            self._output_queue.task_done()
            camera.close()

    def terminate(self):
        """
        Called when task is terminated. Overwrites multiprocessing.Process.terminate() function
        """
        # Set exit event
        self._exit.set()

if __name__ == '__main__':
    output_queue = multiprocessing.Queue()
    cam = Camera(output_queue=output_queue)

    cam.start()

    while True:
        cv2.imshow('camera_image', output_queue.get()['camera_image'])
        cv2.waitKey(1)
