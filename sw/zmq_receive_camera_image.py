import Queue
import multiprocessing
from configobj import ConfigObj
import cv2

from zmq_socket.Subscriber import Subscriber

# Parse confifiguration file
config_file = 'config.ini'
config = ConfigObj(config_file)

# Initialize queues
queues = {'subscriber_out': multiprocessing.Queue()}

# Initialize tasks
sub = Subscriber(output_queue=queues['subscriber_out'],
                 ip='raspberrypi',
                 port=55555)

# Start tasks
sub.start()

while True:
    sub_output = queues['subscriber_out'].get()
    cv2.imshow('camera',sub_output['camera_image'])
    cv2.waitKey(1)
