// C++ (Arduino / Object-Oriented Interface)
#include <Arduino.h>
#include <SPI.h>

class ST7789Display {
private:
    uint8_t cs_pin, dc_pin, rst_pin;
    uint16_t width, height;
    uint16_t x_offset, y_offset;

public:
    ST7789Display(uint8_t cs, uint8_t dc, uint8_t rst, uint16_t w, uint16_t h, uint16_t xo = 0, uint16_t yo = 0)
        : cs_pin(cs), dc_pin(dc), rst_pin(rst), width(w), height(h), x_offset(xo), y_offset(yo) {}

    void init() {
        pinMode(dc_pin, OUTPUT);
        pinMode(rst_pin, OUTPUT);
        if (cs_pin != 0xFF) pinMode(cs_pin, OUTPUT);

        digitalWrite(rst_pin, LOW);
        delayMicroseconds(20);
        digitalWrite(rst_pin, HIGH);
        delay(120);

        writeCommand(0x11); // SLPOUT
        delay(120);

        writeCommand(0x3A); // COLMOD
        writeData(0x55);    // 16-bit RGB565

        writeCommand(0x21); // INVON для IPS Normally Black
        writeCommand(0x29); // DISPON
        delay(50);
    }

    void setAddrWindow(uint16_t x, uint16_t y, uint16_t w, uint16_t h) {
        uint16_t x_start = x + x_offset;
        uint16_t x_end = x + w - 1 + x_offset;
        uint16_t y_start = y + y_offset;
        uint16_t y_end = y + h - 1 + y_offset;

        writeCommand(0x2A);
        uint8_t colBuf[4] = { (uint8_t)(x_start >> 8), (uint8_t)x_start, (uint8_t)(x_end >> 8), (uint8_t)x_end };
        writeData(colBuf, 4);

        writeCommand(0x2B);
        uint8_t rowBuf[4] = { (uint8_t)(y_start >> 8), (uint8_t)y_start, (uint8_t)(y_end >> 8), (uint8_t)y_end };
        writeData(rowBuf, 4);

        writeCommand(0x2C);
    }

private:
    void writeCommand(uint8_t cmd) {
        digitalWrite(dc_pin, LOW);
        SPI.transfer(cmd);
    }

    void writeData(const uint8_t* data, size_t len) {
        digitalWrite(dc_pin, HIGH);
        for (size_t i = 0; i < len; ++i) {
            SPI.transfer(data[i]);
        }
    }
};
