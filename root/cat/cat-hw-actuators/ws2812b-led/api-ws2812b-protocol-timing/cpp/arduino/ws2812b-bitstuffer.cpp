#include <Arduino.h>

// Клас генерації сигналу WS2812B з використанням кодування шаблонів SPI
class WS2812B_BitStuffer {
public:
    // Перетворення 8-бітного колірного значення у 24-бітний шаблон SPI
    static uint32_t byteToSpiPattern(uint8_t colorByte) {
        uint32_t pattern = 0;
        for (int8_t bit = 7; bit >= 0; bit--) {
            pattern <<= 3;
            if ((colorByte >> bit) & 0x01) {
                pattern |= 0b110; // WS2812B біт '1'
            } else {
                pattern |= 0b100; // WS2812B біт '0'
            }
        }
        return pattern;
    }
};
