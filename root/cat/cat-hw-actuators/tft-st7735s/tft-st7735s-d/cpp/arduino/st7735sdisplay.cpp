#include <Arduino.h>
#include <SPI.h>

class ST7735SDisplay {
private:
    uint8_t _cs_pin, _dc_pin, _res_pin;
    uint8_t _offset_x, _offset_y;
    SPIClass *_spi;

    void writeCommand(uint8_t cmd) {
        digitalWrite(_dc_pin, LOW);
        digitalWrite(_cs_pin, LOW);
        _spi->transfer(cmd);
        digitalWrite(_cs_pin, HIGH);
    }

    void writeData(const uint8_t *data, size_t len) {
        digitalWrite(_dc_pin, HIGH);
        digitalWrite(_cs_pin, LOW);
        for (size_t i = 0; i < len; i++) {
            _spi->transfer(data[i]);
        }
        digitalWrite(_cs_pin, HIGH);
    }

public:
    ST7735SDisplay(uint8_t cs, uint8_t dc, uint8_t res, SPIClass &spi = SPI)
        : _cs_pin(cs), _dc_pin(dc), _res_pin(res), _offset_x(2), _offset_y(1), _spi(&spi) {}

    void setAddrWindow(uint16_t x0, uint16_t y0, uint16_t x1, uint16_t y1) {
        uint16_t xs = x0 + _offset_x;
        uint16_t xe = x1 + _offset_x;
        uint16_t ys = y0 + _offset_y;
        uint16_t ye = y1 + _offset_y;

        uint8_t caset[4] = { (uint8_t)(xs >> 8), (uint8_t)(xs & 0xFF), (uint8_t)(xe >> 8), (uint8_t)(xe & 0xFF) };
        writeCommand(0x2A); // CASET
        writeData(caset, 4);

        uint8_t raset[4] = { (uint8_t)(ys >> 8), (uint8_t)(ys & 0xFF), (uint8_t)(ye >> 8), (uint8_t)(ye & 0xFF) };
        writeCommand(0x2B); // RASET
        writeData(raset, 4);

        writeCommand(0x2C); // RAMWR
    }

    void setRotation(uint8_t r) {
        uint8_t madctl = 0x08; // BGR bit set
        switch (r % 4) {
            case 0: madctl |= 0x00; break;
            case 1: madctl |= (0x40 | 0x20); break; // MX | MV
            case 2: madctl |= (0x80 | 0x40); break; // MY | MX
            case 3: madctl |= (0x80 | 0x20); break; // MY | MV
        }
        writeCommand(0x36); // MADCTL
        writeData(&madctl, 1);
    }
};
