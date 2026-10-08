#include <Arduino.h>
#include <SPI.h>

class ST7735SDriver {
private:
    uint8_t _csPin, _dcPin, _rstPin;
    uint8_t _offsetX, _offsetY;

public:
    ST7735SDriver(uint8_t cs, uint8_t dc, uint8_t rst, uint8_t offX = 2, uint8_t offY = 1)
        : _csPin(cs), _dcPin(dc), _rstPin(rst), _offsetX(offX), _offsetY(offY) {}

    void begin() {
        pinMode(_csPin, OUTPUT);
        pinMode(_dcPin, OUTPUT);
        pinMode(_rstPin, OUTPUT);
        digitalWrite(_csPin, HIGH);

        // Апаратне скидання дисплея
        digitalWrite(_rstPin, LOW);
        delay(10);
        digitalWrite(_rstPin, HIGH);
        delay(120);

        SPI.begin();
        
        // Ініціалізація регістрів
        writeCommand(0x01); // SWRESET
        delay(120);
        writeCommand(0x11); // SLPOUT
        delay(120);

        writeCommand(0x3A); // COLMOD
        writeData(0x05);    // 16-біт RGB565

        writeCommand(0x36); // MADCTL
        writeData(0xC8);    // MY=1, MX=1, BGR=1
    }

    void writeCommand(uint8_t cmd) {
        digitalWrite(_dcPin, LOW);
        digitalWrite(_csPin, LOW);
        SPI.transfer(cmd);
        digitalWrite(_csPin, HIGH);
    }

    void writeData(uint8_t data) {
        digitalWrite(_dcPin, HIGH);
        digitalWrite(_csPin, LOW);
        SPI.transfer(data);
        digitalWrite(_csPin, HIGH);
    }

    void setAddrWindow(uint8_t x0, uint8_t y0, uint8_t x1, uint8_t y1) {
        writeCommand(0x2A); // CASET
        writeData(0x00);
        writeData(x0 + _offsetX);
        writeData(0x00);
        writeData(x1 + _offsetX);

        writeCommand(0x2B); // RASET
        writeData(0x00);
        writeData(y0 + _offsetY);
        writeData(0x00);
        writeData(y1 + _offsetY);

        writeCommand(0x2C); // RAMWR
    }
};
