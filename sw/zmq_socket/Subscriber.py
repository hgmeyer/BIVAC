import multiprocessing
import zmq
import msgpack
#import cPickle as pickle
import pickle
import zlib
import time

class Subscriber(multiprocessing.Process):

    def __init__(self, output_queue,
                 ip='localhost', port=55555):

        # Initialize multiprocessing.Process parent
        multiprocessing.Process.__init__(self)

        # Establish queue
        self._output_queue = output_queue

        # Exit event for stopping process
        self._exit = multiprocessing.Event()

        # Initialize variables
        self._ip = ip
        self._port = port

    def run(self):

        # Clear exit event just to be sure
        self._exit.clear()

        # Setup ZMQ subscriber socket
        context = zmq.Context()
        socket = context.socket(zmq.SUB)

        # Subscribe to all messages from server
        socket.setsockopt(zmq.SUBSCRIBE, '')
        server_string = "tcp://" + str(self._ip) + ":" + str(self._port)
        socket.connect(server_string)

        # While exit event is not set...
        while not self._exit.is_set():
            # ...get data from server
            buf = socket.recv()
            data = msgpack.unpackb(buf)

            # ... unpickle and uncompress data
            for key, item in data.iteritems():
                data[key] = pickle.loads(zlib.decompress(item))

            self._output_queue.put(data)

    def terminate(self):
        # Set exit event
        self._exit.set()
