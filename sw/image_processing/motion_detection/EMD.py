"""
Implements image processing by EMD arrays
"""

import multiprocessing

import numpy as np


class EMD(multiprocessing.Process):
    """
    This class implements the processing of camera images by horizontal and vertical EMD arrays.
    """

    def __init__(self,
                 input_queue, output_queue,
                 width, height,
                 lp_rc, lp_dt,
                 hp_rc, hp_dt):
        """
        Constructor of the EMD class

        :param input_queue: multiprocessing.JoinableQueue containing input data
        :param output_queue: multiprocessing.Queue containing output data
        :param width: width of the image/EMD
        :param height: height of the image/EMD
        :param lp_rc: low-pass filter RC
        :param lp_dt: low-pass filter dT
        :param hp_rc: high-pass filter RC
        :param hp_dt: high-pass filter dT
        """
        # Initialize multiprocessing.Process parent
        multiprocessing.Process.__init__(self)

        # Establish queues
        self._input_queue = input_queue
        self._output_queue = output_queue

        # Exit event for stopping process
        self._exit = multiprocessing.Event()

        # Initialize variables
        self._width = width
        self._height = height
        self._lp_rc = lp_rc
        self._lp_dt = lp_dt
        self._hp_rc = hp_rc
        self._hp_dt = hp_dt

        self._img = np.zeros(shape=(height, width), dtype=np.int8)
        self._oldimg = self._img
        self._hpimg = self._img
        self._lpimg = self._img

    def run(self):
        """
        Function called when task is started (e.g. task.start()). Overrides run function of multiprocessing. Process
        parent
        """
        # Clear exit event just to be sure
        self._exit.clear()

        # While exit event is not set...
        while not self._exit.is_set():
            # Get previous image
            self._oldimg = self._img

            # Get data from input queue
            self._parse_input()

            # Apply temporal high-pass filter to image
            self._hpimg = self._hp_filter(self._hpimg,
                                          self._oldimg,
                                          self._img,
                                          self._hp_rc,
                                          self._hp_dt)

            # Apply temporal low-pass filter to image
            self._lpimg = self._lp_filter(self._lpimg,
                                          self._hpimg,
                                          self._lp_rc,
                                          self._lp_dt)

            # Correlate signals
            hmult_l, vmult_u, hmult_r, vmult_d = self._multiply_neighbours(self._lpimg, self._hpimg)

            # Compute horizontal and vertical eemd output
            hemd = hmult_l - hmult_r
            vemd = vmult_u - vmult_d

            # Compute contrast-weighted nearness map
            nearness_map = np.log(np.multiply(hemd, hemd) + np.multiply(vemd, vemd) + np.exp(0))

            # - Compute average distance -
            # Sum EMD output array along vertical extent to obtain average nearness array
            avg_nearness = np.sum(nearness_map, axis=0)

            # Normalize average nearness array
            avg_nearness_normalized = avg_nearness - np.min(avg_nearness)
            avg_nearness_normalized /= np.max(avg_nearness_normalized)

            # Compute average distance by inverting the array
            avg_distance = np.max(avg_nearness_normalized) - avg_nearness_normalized

            # - Compute Center of Mass Average Nearness Vector (COMANV) -
            # Initialize azimuth according to horizontal extent of the average distance array assuming 360 degree
            azimuth = np.linspace(np.pi, -np.pi, avg_distance.shape[0])

            # # Scale and rotate the azimuth according to the FOV of the camera and the robot orientation
            # azimuth_scale = self._rotation[0] * (np.pi / 180) + azimuth / self._fov_scaling_factor

            # Compute COMANV
            comanv_x = np.cos(azimuth)
            comanv_y = np.sin(azimuth)
            comanv_x = np.multiply(avg_distance, comanv_x)
            comanv_y = np.multiply(avg_distance, comanv_y)
            comanv_x = np.sum(comanv_x)
            comanv_y = np.sum(comanv_y)
            comanv = [comanv_x, comanv_y]

            # Put data in output queue
            data = {'nearness_map': nearness_map,
                    'nearness_map_normalized': self.float2uint8(nearness_map),
                    'COMANV': comanv}
            self._output_queue.put(data)

        # If exit event set...
        if self._exit.is_set():
            # ...shutdown
            self._input_queue.task_done()
            self._output_queue.task_done()

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

        # Check if new data is available
        if data is not None:
            # Parse data from input queue
            try:
                self._img = data['remapped_image']
            except KeyError as e:
                raise KeyError('Key ' + e.args[0] + ' not found in input data!')

    @staticmethod
    def _lp_filter(oldout, newin, rc, dt):
        alpha = dt / (rc + dt)
        return np.round(alpha * newin + (1 - alpha) * oldout, 1)

    @staticmethod
    def _hp_filter(oldout, oldin, newin, rc, dt):
        alpha = rc / (rc + dt)
        return np.round(alpha * (oldout + newin - oldin), 1)

    @staticmethod
    def _multiply_neighbours(frame, framen):
        framenshifteddown = np.roll(framen, 1, axis=0)
        framenshiftedright = np.roll(framen, 1, axis=1)
        framenshiftedup = np.roll(framen, -1, axis=0)
        framenshiftedleft = np.roll(framen, -1, axis=1)

        hrzmultright = np.multiply(frame, framenshiftedleft)
        hrzmultleft = np.multiply(frame, framenshiftedright)
        vertmultdown = np.multiply(frame, framenshiftedup)
        vertmultup = np.multiply(frame, framenshifteddown)

        hrzmultleft = np.roll(hrzmultleft, -1, axis=1)

        vertmultup = np.roll(vertmultup, -1, axis=0)
        np.roll(framen, 1, axis=0)

        return hrzmultleft, vertmultup, hrzmultright, vertmultdown

    # Normalise data to uint8
    @staticmethod
    def float2uint8(image):
        minval = np.amin(image)
        maxval = np.amax(image)
        image = (image - minval) / (maxval - minval)
        image *= 255
        image = image.astype('uint8')
        return image
