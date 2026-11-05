#include <SPI.h>

const int pinPL = 5;

void setup() {
    pinMode(pinPL, OUTPUT);
    digitalWrite(pinPL, HIGH);
    SPI.begin();
}

uint8_t read_74hc165() {
    digitalWrite(pinPL, LOW);
    digitalWrite(pinPL, HIGH);
    
    SPI.beginTransaction(SPISettings(1000000, MSBFIRST, SPI_MODE0));
    uint8_t data = SPI.transfer(0x00);
    SPI.endTransaction();
    
    return data;
}
