import Queue
import multiprocessing
from configobj import ConfigObj
import cv2

from camera.webcam.WebCamClient import Camera
#from camera.picamera.PiCameraClient import Camera
from image_processing.remapping.Unwarper import Unwarper
from image_processing.motion_detection.EMD import EMD
from calibration.Calibration import Calibration
from zmq_socket.Publisher import Publisher
from zmq_socket.Subscriber import Subscriber

# Parse confifiguration file
config_file = 'config.ini'
config = ConfigObj(config_file)

# Initialize queues
queues = {'camera_out': multiprocessing.Queue(),
          'unwarper_in': multiprocessing.JoinableQueue(),
          'unwarper_out': multiprocessing.Queue(),
          'emd_in': multiprocessing.JoinableQueue(),
          'emd_out': multiprocessing.Queue(),
          'calibration_in': multiprocessing.JoinableQueue(),
          'zmq_socket_in': multiprocessing.JoinableQueue(),
          'zmq_socket_out': multiprocessing.Queue()}

# Initialize tasks
print map(int, config['Camera']['roi_vertical'])
camera = Camera(output_queue=queues['camera_out'],
                camera_port=config.get('Camera').as_int('port'),
                #roi_vertical=map(int, config['Camera']['roi_vertical']),
                #roi_horizontal=map(int, config['Camera']['roi_horizontal'])
                )

'''
unwarper = Unwarper(input_queue=queues['unwarper_in'],
                    output_queue=queues['unwarper_out'],
                    width_rescaled=,
                    height_rescaled=,
                    scaling_factor=,
                    calibration_file=)

emd = EMD(input_queue=queues['emd_in'],
          output_queue=queues['emd_out'],
          width=,
          height=,
          lp_rc=,
          lp_dt=,
          hp_rc=,
          hp_dt=)

calibration = Calibration(input_queue=queues['calibration_in'],
                          calibration_file=None)
'''

pub = Publisher(input_queue=queues['zmq_socket_in'])
sub = Subscriber(output_queue=queues['zmq_socket_out'])


# Start tasks
camera.start()
#unwarper.start()
#emd.start()
#calibration.start()
pub.start()
sub.start()

while True:
    camera_output = queues['camera_out'].get()
    queues['zmq_socket_in'].put(camera_output)
    sub_output = queues['zmq_socket_out'].get()
    cv2.imshow('camera',sub_output['camera_image'])
    cv2.waitKey(1)
