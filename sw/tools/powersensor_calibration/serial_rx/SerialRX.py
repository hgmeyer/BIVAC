# SerialRX - A multiprocessing process for receiving data from a serial port
# Copyright (C) 2016 Hanno Gerd Meyer <hanno@neuromail.de>
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of  MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.

import multiprocessing
import Queue

import serial


class SerialRX(multiprocessing.Process):
    """
    A process that receives data from a serial port an puts it into a multiprocessing queue.
    """

    def __init__(self, output_queue, port, baudrate=115200):
        """
        Constructor of the SerialRX class

        :param output_queue: multiprocessing.Queue containing the data received from serial port
        :param port: specifies the serial port
        :param baudrate: specifies the baudrate
        """

        # Initialize multiprocessing.Process parent
        multiprocessing.Process.__init__(self)

        # Establish input queue
        self._output_queue = output_queue

        # Exit event for stopping process
        self._exit = multiprocessing.Event()

        # Initialize variables
        self._port = port
        self._baudrate = baudrate

    def run(self):
        """
        Function called when task is started (e.g. task.start()). Overrides run function of multiprocessing.Process
        parent
        """

        # Clear exit event just to be sure
        self._exit.clear()

        # Initialize serial object
        s = serial.Serial(port=self._port,
                          baudrate=self._baudrate,
                          timeout=None)

        # While exit event is not set...
        while not self._exit.is_set():
            if s.inWaiting():
                self._clear_queue(self._output_queue)
                buf = s.readline().strip('\n')
                self._output_queue.put(buf)

    def terminate(self):
        """
        Called when task is terminated. Overwrites multiprocessing.Process.terminate() function
        """
        # Set exit event
        self._exit.set()

    @staticmethod
    def _clear_queue(some_queue):
        """
        Clears the multiprocessing queue passed to the method

        :param some_queue: multiprocessing.Queue to be cleared
        """

        while not some_queue.empty():
            try:
                some_queue.get_nowait()
            except Queue.Empty:
                pass

if __name__ == '__main__':
    import argparse

    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port',
                        default='/dev/ttyACM0',
                        type=str,
                        dest='port',
                        help='Specify the serial port')
    parser.add_argument('-b', '--baudrate',
                        default=115200,
                        type=int,
                        dest='baudrate',
                        help='Specify baudrate')
    args = parser.parse_args()

    # Initialize an output queue
    output_queue = multiprocessing.Queue()

    # Initialize and start SerialRX process
    serialrx = SerialRX(output_queue=output_queue,
                        port=args.port,
                        baudrate=args.baudrate)
    serialrx.start()

    # Print data reveived
    while True:
        data = output_queue.get()
        data = 8.829e-05 * float(data) + 0.009475
        print '{:2.2f}V'.format(data)
