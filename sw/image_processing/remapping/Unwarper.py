"""
Implements a task for unwarping the camera images
"""

import multiprocessing

import cv2
from image_processing.remapping.OCameraModel import OCameraModel


class Unwarper(multiprocessing.Process):
    """
    This class implements a task for unwarping the images obtained from a camera with a fisheye lens
    """

    def __init__(self, input_queue, output_queue,
                 width_rescaled, height_rescaled,
                 scaling_factor,
                 calibration_file,
                 flip_image=False):
        """
        Constructor of the Unwarping class

        :param input_queue: multiprocessing.JoinableQueue containing input data
        :param output_queue: multiprocessing.Queue containing output data
        :param width_rescaled: width of the remapped image
        :param height_rescaled: height of the remapped image
        :param flip_image: flips the image upside down if set to true
        :param calibration_file: calibration file (from OCamModel toolbox) containing camera calibration data
        """

        # Initialize multiprocessing.Process parent
        multiprocessing.Process.__init__(self)

        # Establish queues
        self._input_queue = input_queue
        self._output_queue = output_queue

        # Exit event for stopping process
        self._exit = multiprocessing.Event()

        # Initialize variables
        self._img = None
        self._width_rescaled = width_rescaled
        self._height_rescaled = height_rescaled
        self._flip_image = flip_image
        self._scaling_factor = scaling_factor
        self._calibration_file = calibration_file

        # Initialize omidirectional camera model
        self._ocammodel = OCameraModel()

        # Parse calibration file
        self._ocammodel.get_ocam_model(self._calibration_file)

        # Get undistortion LUTs
        self._mapx, self._mapy = self._ocammodel.create_perspective_undistortion_lut(self._height_rescaled,
                                                                                     self._width_rescaled,
                                                                                     self._scaling_factor)

    def run(self):
        """
        Function called when task is started (e.g. task.start()). Overrides run function of multiprocessing. Process
        parent
        """
        # Clear exit event just to be sure
        self._exit.clear()

        # While exit event is not set...
        while not self._exit.is_set():
            # ...get data from input queue
            self._parse_input()

            # ...remap image
            img_remapped = cv2.remap(self._img, self._mapx, self._mapy, cv2.INTER_AREA)

            # ...flip image
            if self._flip_image:
                img_remapped = cv2.flip(img_remapped, 0)
                img_remapped = cv2.flip(img_remapped, 1)

            # ...put image in output queue
            self._output_queue.put(({'remapped_image': img_remapped}))

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
                raise KeyError('Key ' + e.args[0] + ' not found in input data!')
