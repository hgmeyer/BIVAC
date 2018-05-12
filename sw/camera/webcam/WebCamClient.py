"""
A client for getting images from a webcam.
"""

import multiprocessing
import cv2
import numpy as np


class Camera(multiprocessing.Process):
    """
    Implements a task for fetching camera images from a webcam.
    """

    def __init__(self, output_queue,
                 camera_port=0,
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

        # Get camera port
        self._camera_port = camera_port

        # Get ROI coordinates
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
        camera = cv2.VideoCapture(self._camera_port)

        # While exit event is not set...
        while not self._exit.is_set():
            s, buf = camera.read()
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
    cam = Camera(output_queue=output_queue,
                       camera_port=0)

    cam.start()

    while True:
        cv2.imshow('camera_image', output_queue.get()['camera_image'])
        cv2.waitKey(1)
