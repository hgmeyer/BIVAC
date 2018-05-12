"""
Implements a task for obtaining omidirectional lens calibration data
"""

import multiprocessing
import cv2
import numpy as np


class Calibration(multiprocessing.Process):
    """
    This class implements a task for obtaining calibration data for a omnidirectional lens
    """

    def __init__(self, input_queue,
                 calibration_file):
        """
        Constructor of the Calibration class

        :param input_queue: multiprocessing.JoinableQueue containing input data

        """

        # Initialize multiprocessing.Process parent
        multiprocessing.Process.__init__(self)

        # Establish queues
        self._input_queue = input_queue


        # Exit event for stopping process
        self._exit = multiprocessing.Event()

        # Initialize variables
        self._img = None
        self._calibration_file = calibration_file

    def run(self):
        """
        Function called when task is started (e.g. task.start()). Overrides run function of multiprocessing. Process
        parent
        """
        # Clear exit event just to be sure
        self._exit.clear()

        # termination criteria
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

        # Prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
        objp = np.zeros((6*7,3), np.float32)
        objp[:,:2] = np.mgrid[0:7,0:6].T.reshape(-1,2)

        # Arrays to store object points and image points from all the images.
        objpoints = [] # 3d point in real world space
        imgpoints = [] # 2d points in image plane.

        # While exit event is not set...
        while not self._exit.is_set():
            # ...get data from input queue
            self._parse_input()

            # ...find the chess board corners
            ret, corners = cv2.findChessboardCorners(self._img, (9,6),None)

            # If found, add object points, image points (after refining them)
            if ret == True:
                objpoints.append(objp)

                #cv2.cornerSubPix(self._img,corners,(11,11),(-1,-1),criteria)
                imgpoints.append(corners)

                # Draw and display the corners
                cv2.drawChessboardCorners(self._img, (7,6), corners, ret)
                cv2.imshow('img',self._img)
                cv2.waitKey(500)

    def terminate(self):
        """
        Called when task is terminated. Overwrites multiprocessing.Process.terminate() function
        """
        # Set exit event
        self._exit.set()

    def _parse_input(self):
        """
        Parse data from input queue
        """
        # Get data from queue
        data = self._input_queue.get()

        if data is not None:
            # Parse data from input queue
            try:
                self._img = data['camera_image']
            except KeyError as e:
                raise KeyError(
                    'Key ' + e.args[0] + ' not found in input data!')
