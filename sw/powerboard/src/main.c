#include <avr/io.h>
#include <util/delay.h>

#include <config.h>
#include <usiTwiSlave.h>

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

        // Wait for ADC register changes to settle
        _delay_ms(10);
}

int get_raw_ADC()
{
        uint8_t adc_low;

        // Start ADC measurement
        ADCSRA |= (1 << ADSC);

        // Wait until conversion complete
        while (ADCSRA & (1 << ADSC)) ;

        // Get low byte of ADC measurement
        adc_low = ADCL;

        // Return merged low and high byte
        return (ADCH << 8 | adc_low) * 64; //multiply by 64 to scale up to 16 bit
}

int get_raw_ADC_moving_average(int sample_n, int sample_window)
{
        uint16_t raw_adc_moving_average;

        for(int i=0; i<sample_n; i++)
        {
                // Initialize moving average with ADC reading
                raw_adc_moving_average = get_raw_ADC();
                // Caluclate integrated moving average
                raw_adc_moving_average += (get_raw_ADC() - raw_adc_moving_average) / sample_window;
        }

        return raw_adc_moving_average;
}

int main(void)
{
        uint16_t adc_buffer;

        // Initialize ADC
        initADC();

        // make the LED pin an output for PORTB4
        DDRB = 1 << 4;

        // Main loop
        while (1)
        {
                // Set ADC3 as single-ended input in ADMUX
                ADMUX |= (0 << MUX3) | (0 << MUX2) | (1 << MUX1) | (1 << MUX0);

                // Get ADC measurement
                //adc_buffer = get_raw_ADC();
                adc_buffer = get_raw_ADC_moving_average(SAMPLE_N, SAMPLE_WINDOW);

                if (adc_buffer > 32768)
                {
                        PORTB |= (1 << 4);
                }

                else
                {
                        PORTB &= ~(1 << 4);
                }

                // Write ADC3 measurement in TWI TX-buffer
                txbuffer[0] = adc_buffer;
                txbuffer[1] = adc_buffer >> 8;
        }

        return 0;
}
