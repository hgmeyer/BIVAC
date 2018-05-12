#import cPickle as pickle
import pickle
import msgpack
import multiprocessing
import zlib
import zmq
import time


class Publisher(multiprocessing.Process):

    def __init__(self, input_queue, ip='*', port=55555, append_timestamp=True):
        """
        Constructor of the Publisher class.

        :param input_queue: multiprocessing.Queue containing input data
        :param ip: IP address of the publisher socket
        :param port: port of the publisher socket
        """

        # Initialize multiprocessing.Process parent
        multiprocessing.Process.__init__(self)

        # Establish queue
        self._input_queue = input_queue

        # Exit event for stopping process
        self._exit = multiprocessing.Event()

        # Initialize variables
        self._ip = ip
        self._port = port
        self._data = None
        self._append_timestamp = append_timestamp

    def run(self):
        """
        Function called when task is started (e.g. task.start()). Overrides run function of multiprocessing.Process
        parent
        """

        # Clear exit event just to be sure
        self._exit.clear()

        # Setup 0MQ publisher socket for sending data from the server
        context = zmq.Context()
        socket = context.socket(zmq.PUB)
        server_string = "tcp://" + str(self._ip) + ":" + str(self._port)
        socket.bind(server_string)

        # While exit event is not set...
        while not self._exit.is_set():
            # ...clear input queue
            self._clear_queue(self._input_queue)

            # Get data from input queue
            self._parse_input(append_timestamp=self._append_timestamp)

            if self._data is not None:
                # Pack data into message
                msg = msgpack.packb(self._data)

                # Publish message
                try:
                    socket.send(msg)
                    self._data = None
                except zmq.ZMQError as e:
                    print('Could not send message via 0MQ with error: %s' % e)

    def terminate(self):
        """
        Called when task is terminated. Overwrites multiprocessing.Process.terminate() function
        """
        # Set exit event
        self._exit.set()

    def _parse_input(self, append_timestamp=False):
        """
        Parse data from input queue
        """
        # Get data from queue
        self._data = self._input_queue.get()

        if self._data is not None:
            if append_timestamp:
                self._data['t_stamp']=time.time()
                print self._data['t_stamp']
            # For every item in data dict
            for key, item in self._data.items():
                self._data[key] = zlib.compress(
                    pickle.dumps(self._data[key], protocol=0))
        else:
            pass

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
