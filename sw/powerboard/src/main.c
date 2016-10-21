#include <avr/io.h>
#include <util/delay.h>

#include <config.h>
#include <usiTwiSlave.h>


// Set CPU frequency
#ifndef F_CPU
#define F_CPU 8000000UL // 8 MHz
#endif

int main(void)
{
        while (1)
        {
                _delay_ms(SAMPLERATE);

                txbuffer[0] = 1;
                txbuffer[1] = 2;
                txbuffer[2] = 3;
        }

        return 0;
}
