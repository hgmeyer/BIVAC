#ifndef _CONFIG_H_
#define _CONFIG_H_

// Define I2C adress of slave (Note: LSB is the I2C r/w flag and must not be used for addressing!)
#define SLAVE_ADDR  0b00001000  // 0x04

// Define number of samples to compute moving average from
#define SAMPLE_N 128
// Define window size of moving average
#define SAMPLE_WINDOW 128

#endif  // ifndef _CONFIG_H_
