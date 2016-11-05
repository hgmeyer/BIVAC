#include <avr/io.h>
#include <avr/interrupt.h>
#include <util/delay.h>

#include <config.h>
#include <usiTwiSlave.h>

void initTimer(void)
{
        // Set timer to CTC mode
        TCCR0A |= (1 << WGM01);

        // Set prescaler to 1024
        TCCR0B |= (1 << CS02)|(1 << CS00);

        // Initialize counter
        TCNT0 = 0;

        // Set compare value corresponding to approx. 100.16Hz
        OCR0A = 78; // TODO: Multiply sample rate by number of ADCs used.

        // Enable compare interrupt
        TIMSK |= (1 << OCIE0A);
}

void initADC(void)
{
        // Set ADMUX register
        ADMUX =
                (0 << ADLAR) |  // do not left shift (10bit)
                (0 << REFS2) |  // set reference voltage to 1.1 V
                (1 << REFS1) |
                (0 << REFS0) |
                (0 << MUX3)  |  // set ADC3 as input
                (0 << MUX2)  |
                (1 << MUX1)  |
                (1 << MUX0);

        // Set ADCSRA register
        ADCSRA =
                (1 << ADEN)  |  // enable ADC
                (1 << ADPS2) |  // set prescaler to 64 (125kHz)
                (1 << ADPS1) |
                (0 << ADPS0);
}

ISR (TIMER0_COMPA_vect)
{
        // Start ADC measurement
        ADCSRA |= (1 << ADSC);
}

int main(void)
{
        uint16_t adc_buffer;
        uint8_t adc_lowbyte;

        uint8_t adc_n = 0;

        // Calibrate clock
        OSCCAL -= 0;

        // Disable interrupts
        cli();

        // Initialize timer
        initTimer();

        // Initialize ADC
        initADC();

        // Enable I2C slave
        usiTwiSlaveInit(SLAVE_ADDR);

        // Enable interrupts
        sei();

        // Main loop
        while (1)
        {
                // If ADC measurement has been completed
                if ((ADCSRA & (1 << ADSC)) == 0)
                {
                        // Get low byte of ADC measurement
                        adc_lowbyte = ADCL;

                        // Scale 10 Bit measurement to 16 Bit
                        adc_buffer = (ADCH << 8 | adc_lowbyte) * 64;

                        // Switch write current measurement to buffer and switch to next ADC
                        if (adc_n < 1) {
                                switch (adc_n) {
                                case 0:
                                        txbuffer[0] = adc_buffer;
                                        txbuffer[1] = adc_buffer >> 8;
                                        ADMUX |= (0 << MUX3) | (0 << MUX2) | (1 << MUX1) | (1 << MUX0);
                                        break;
                                }
                        }
                        else{
                                adc_n = 0;
                        }
                }

        }

        return 0;
}
