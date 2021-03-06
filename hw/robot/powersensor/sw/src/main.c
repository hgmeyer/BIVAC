/*
 * PowerSensor v0.2 firmware
 * Copyright (C) 2016 Hanno Gerd Meyer <hanno@neuromail.de>
 *
 * This program is free software: you can redistribute it and/or modify it
 * under the terms of the GNU General Public License as published by the Free
 * Software Foundation, either version 3 of the License, or (at your option)
 * any later version.
 *
 * This program is distributed in the hope that it will be useful, but WITHOUT
 * ANY WARRANTY; without even the implied warranty of  MERCHANTABILITY or
 * FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
 * more details.
 *
 * You should have received a copy of the GNU General Public License along with
 * this program.  If not, see <http://www.gnu.org/licenses/>.
 */

#include <avr/io.h>
#include <avr/interrupt.h>
#include <util/delay.h>
#include <usiTwiSlave.h>

#ifndef DEBUG
#define DEBUG 0
#endif

// Define I2C adress of slave (Note: LSB is the I2C r/w flag and must not be used for addressing!)
#define SLAVE_ADDR  0b00001000  // 0x04

// The number of ADC channels to be multiplexed
#define ADC_N   5

// ADC channel and index variables
uint8_t adc_channels[ADC_N] = {0, 1, 2, 3, 7}; // PA0, PA1, PA2, PA3, PA7
uint8_t adc_index = 0;

// ADC buffer
uint16_t adc_buffer;
uint8_t adc_lowbyte;

void initTimer(void)
{
        // Set timer to CTC mode
        TCCR0A |= (1 << WGM01);

        // Set prescaler to 64
        TCCR0B |= (1 << CS01)|(1 << CS00);

        // Initialize counter
        TCNT0 = 0;

        // Set compare value corresponding to 500Hz (100Hz per Channel)
        OCR0A = 250;

        // Enable compare interrupt
        TIMSK0 |= (1 << OCIE0A);
}

void initADC(void)
{
        // Set reference voltage to 1.1V
        ADMUX |= (1 << REFS1);

        // Clear MUX0:5 and set adc channel according to current index
        ADMUX = (ADMUX & ~(0x3F)) | (adc_channels[adc_index] & 0x3F);

        // Enable ADC
        ADCSRA |= (1 << ADEN);

        // Set prescaler to 64 (125kHz)
        ADCSRA |= (1 << ADPS2) |
                  (1 << ADPS1);
}

ISR (TIM0_COMPA_vect)
{
        // Start ADC measurement
        ADCSRA |= (1 << ADSC);

        if(DEBUG) {
                // Toggle PB0
                PORTB ^= (1 << PB0);
        }
}

int main(void)
{

        if(DEBUG) {
                // Set PB0 and PB1 as output pins
                DDRB |= (1<<PB0) | (1<<PB1);
        }

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
                        if (DEBUG) {
                                // Toggle PB1
                                PORTB ^= (1 << PB1);
                        }

                        // Get low byte of ADC measurement
                        adc_lowbyte = ADCL;

                        // Scale 10 Bit measurement to 16 Bit
                        adc_buffer = (ADCH << 8 | adc_lowbyte) * 64;

                        // Write ADC measurement to buffer
                        txbuffer[adc_index+adc_index] = adc_buffer;
                        txbuffer[adc_index+adc_index+1] = adc_buffer >> 8;

                        // Set ADC index
                        if (adc_index < ADC_N-1) {
                                adc_index += 1;
                        }
                        else{
                                adc_index = 0;
                        }

                        // Clear MUX0:5 and set ADC channel
                        ADMUX = (ADMUX & ~(0x3F)) | (adc_channels[adc_index] & 0x3F);

                        // Wait until next ADC measurement starts
                        while((ADCSRA & (1 << ADSC)) == 0) {}
                }
        }

        return 0;
}
