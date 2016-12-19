# A simple Python script for calibrating the PowerSensor board.
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
import sys
import time
from ctypes import *

import numpy as np

from dwf.dwfconstants import *
from matplotlib import pyplot as plt
from pyusbtmc.instrument import usbtmc
from serial_rx.SerialRX import SerialRX

# - PARAMETERS -
# -- General ---
# Number of samples per voltage step
n_per_step = 50

# Delay between samples
d_per_sample = 0.05  # s

# Delay after voltage step
d_after_step = 1.0  # s

# Range of voltages to be tested
voltage_range = [0.0, 4.5]  # V

# Voltage increment per step
voltage_inc = 0.1  # V

# Port of the multimeter
mm_port = '/dev/usbtmc2'

# Port of the Arduino
s_port = '/dev/ttyACM0'

# Baudrate of the Arduino
s_baudrate = 115200


# - CALIBRATION SCRIPT -
# Initialize array with voltage values
voltages = np.arange(voltage_range[0],
                     voltage_range[1] + voltage_inc,
                     voltage_inc)

# Initialize numpy array for storing measurements
measurements = np.zeros([2, len(voltages), n_per_step])

# Initialize separate process for receiving I2C data from Arduino via
# serial port
print 'Spawning process for receiving serial data...'
serial_output_queue = multiprocessing.JoinableQueue()
serialrx = SerialRX(output_queue=serial_output_queue,
                    port=s_port,
                    baudrate=s_baudrate)
serialrx.start()

# Open Rigol Multimeter
print 'Opening Multimeter...'
mm = usbtmc(device=mm_port)

# Load Digilent Waveforms API
dwf = cdll.LoadLibrary("libdwf.so")

# Declare Digilent Waveforms ctype variables
hdwf = c_int()
channel = c_int(0)

# Open Analog Discovery 2
print 'Opening Analog Discovery device...'
dwf.FDwfDeviceOpen(c_int(-1), byref(hdwf))
if hdwf.value == hdwfNone.value:
    print 'Failed to open device'
    quit()

# Enable analog out carrier node
dwf.FDwfAnalogOutNodeEnableSet(
    hdwf, channel, AnalogOutNodeCarrier, c_bool(True))

# Set AnalogOutNodeCarrier to DC mode
dwf.FDwfAnalogOutNodeFunctionSet(hdwf, channel, AnalogOutNodeCarrier, funcDC)

# Set voltage to 0.0V
dwf.FDwfAnalogOutNodeOffsetSet(
    hdwf, channel, AnalogOutNodeCarrier, c_double(0.0))

for i in xrange(0, len(voltages)):
    # Set voltage
    print 'Setting voltage to: ' + str(voltages[i]) + 'V'
    dwf.FDwfAnalogOutNodeOffsetSet(
        hdwf, channel, AnalogOutNodeCarrier, c_double(voltages[i]))
    #dwf.FDwfAnalogOutConfigure(hdwf, channel, c_bool(True))
    time.sleep(d_after_step)

    for j in xrange(0, n_per_step):

        # Get multimeter voltage
        mm.write(':MEAS:VOLT:DC?')
        v_mm = mm.read()
        measurements[0, i, j] = float(v_mm)

        # Get sensorboard voltage
        measurements[1, i, j] = serial_output_queue.get()

        print 'Read: {} - {}'.format(measurements[1, i, j], measurements[0, i, j])

        # Sleep for some time
        time.sleep(d_per_sample)

# Close devices
dwf.FDwfDeviceClose(hdwf)

# Fit linear regression
fit = np.polyfit(measurements[1, :, :].flatten(),
                 measurements[0, :, :].flatten(), 1)
fit_fn = np.poly1d(fit)

print '\n--- RESULTS ---'
print 'Transfer function: ' + str(fit_fn)
print 'a: {}, b: {}'.format(fit[1], fit[0])

bit_range = range(0, 2**16, 100)

plt.plot(measurements[1, :, :], measurements[0, :, :], 'or',
         bit_range, fit_fn(bit_range), '--k')
plt.show()
