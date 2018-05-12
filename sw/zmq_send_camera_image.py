import Queue
import multiprocessing
from configobj import ConfigObj
import cv2

from camera.picamera.PiCameraClient import Camera
from zmq_socket.Publisher import Publisher


# Parse confifiguration file
config_file = 'config.ini'
config = ConfigObj(config_file)

# Initialize queues
queues = {'camera_out': multiprocessing.Queue(),
          'publisher_in': multiprocessing.JoinableQueue()
          }

# Initialize tasks
camera = Camera(output_queue=queues['camera_out'],
                #roi_vertical=map(int, config['Camera']['roi_vertical']),
                #roi_horizontal=map(int, config['Camera']['roi_horizontal'])
                )

pub = Publisher(input_queue=queues['publisher_in'])

# Start tasks
camera.start()
pub.start()

while True:
    camera_output = queues['camera_out'].get()
    queues['publisher_in'].put(camera_output)
