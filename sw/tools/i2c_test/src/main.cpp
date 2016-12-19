#include <Arduino.h>
#include <Wire.h>

byte read_address = 0x04;
volatile int buffer[10];
volatile uint16_t value_raw;

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

        value_raw = (buffer[0] | buffer[1]<<8);
        Serial.println(value_raw);
        delay(10);
}
