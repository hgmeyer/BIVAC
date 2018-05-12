#include <avr/io.h>
#include <avr/interrupt.h>
#include <util/delay.h>
#include <usiTwiSlave.h>

// Define I2C adress of slave (Note: LSB is the I2C r/w flag and must not be used for addressing!)
#define SLAVE_ADDR  0b00001000  // 0x04

/* Initializes 16-Bit Timer1 for generating phase-correct PWM signal on OC1B pin */
void initPWMTimer(void){

        // * Set Timer1 to PWM mode 10: phase-correct, ICR1 defines top
        // * Clear OC1B on Compare Match when upcounting. Set OC1B on Compare Match when downcounting.
        // * Set prescaler to
        TCCR1A |= (1 << COM1B1) | (1 << WGM11);
        TCCR1B |= (1 << WGM13) | (1 << CS11) |(1 << CS10);

        // Set OC1B pin (PA5) as output
        DDRA  |= (1 << PA5);

        // Set Timer1 top to 16-bit MAX
        ICR1 = 0xFFFF;

        // Set duty cycle to 0%
        OCR1B = 0x0000;

        /*
           // TODO: Use 16-Bit timer1 for more fine-grained PWM control

           // Set OC0A (DDB2) as output pin
           DDRB = 1 << DDB2;

           // PWM mode 1: phase-correct, fixed top
           // Set OC0A on Compare Match when up-counting. Clear OC0A on compare Match when down-counting.
           TCCR0A = (1<<COM0A1) | (1<<COM0B0) | (1<<WGM00);

           // Set prescaler
           TCCR0B |= (1 << CS00);

           // Set duty cycle to 50%
           OCR0A = 0;
         */
}



void initSampleTimer(){
}

void setPWM(uint16_t pwm){
        OCR1B = pwm;
}

int main(void){
        // Disable interrupts
        cli();

        // Enable I2C slave
        usiTwiSlaveInit(SLAVE_ADDR);

        initPWMTimer();

        // Re-Enable interrupts
        sei();

        setPWM(0x00FF);

        while(1) {

        }
        return 0;
}
