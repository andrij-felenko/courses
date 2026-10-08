#include <Arduino.h>
#include <SPI.h>

void initST7735SDisplay(uint8_t cs, uint8_t dc, uint8_t res) {
    pinMode(cs, OUTPUT);
    pinMode(dc, OUTPUT);
    pinMode(res, OUTPUT);

    // Апаратне скидання (Hardware Reset)
    digitalWrite(res, LOW);
    delay(10);
    digitalWrite(res, HIGH);
    delay(120);

    // Програмне скидання та вихід зі сну
    digitalWrite(dc, LOW); digitalWrite(cs, LOW); SPI.transfer(0x01); digitalWrite(cs, HIGH); // SWRESET
    delay(120);

    digitalWrite(dc, LOW); digitalWrite(cs, LOW); SPI.transfer(0x11); digitalWrite(cs, HIGH); // SLPOUT
    delay(120);

    // Конфігурація форматів та драйверів живлення
    digitalWrite(dc, LOW); digitalWrite(cs, LOW); SPI.transfer(0x3A); digitalWrite(cs, HIGH); // COLMOD
    digitalWrite(dc, HIGH); digitalWrite(cs, LOW); SPI.transfer(0x05); digitalWrite(cs, HIGH); // 16-bit RGB565

    digitalWrite(dc, LOW); digitalWrite(cs, LOW); SPI.transfer(0x36); digitalWrite(cs, HIGH); // MADCTL
    digitalWrite(dc, HIGH); digitalWrite(cs, LOW); SPI.transfer(0x08); digitalWrite(cs, HIGH); // BGR

    // Увімкнення дисплея (Display ON)
    digitalWrite(dc, LOW); digitalWrite(cs, LOW); SPI.transfer(0x29); digitalWrite(cs, HIGH); // DISPON
    delay(100);
}
