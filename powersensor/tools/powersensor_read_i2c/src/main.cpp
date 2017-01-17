#include <Arduino.h>
#include <Wire.h>

byte read_address = 0x04;
volatile int buffer[10];

void setup() {
        Serial.begin(115200);
        Wire.begin();
        Wire.setClock(400000UL);
}

void loop() {
        Wire.beginTransmission(read_address);
        Wire.endTransmission();
        Wire.requestFrom(read_address, 10);

        int i = 0;
        while (Wire.available())
        {
                buffer[i] = Wire.read();
                i++;
        }

        Serial.print((uint16_t)(buffer[0] | buffer[1]<<8));
        Serial.print(' ');
        Serial.print((uint16_t)(buffer[2] | buffer[3]<<8));
        Serial.print(' ');
        Serial.print((uint16_t)(buffer[4] | buffer[5]<<8));
        Serial.print(' ');
        Serial.print((uint16_t)(buffer[6] | buffer[7]<<8));
        Serial.print(' ');
        Serial.print((uint16_t)(buffer[8] | buffer[9]<<8));
        Serial.print('\n');
        delay(10);
}
