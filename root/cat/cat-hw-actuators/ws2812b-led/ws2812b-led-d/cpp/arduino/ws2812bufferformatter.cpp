// Приклад концептуальної упакованої структури буфера світлодіодного кадру (Arduino / C++)
#include <Arduino.h>

class WS2812BufferFormatter {
public:
    static void formatGRBBitstream(uint8_t red, uint8_t green, uint8_t blue, uint8_t* targetBuffer) {
        uint32_t colorPattern = ((uint32_t)green << 16) | ((uint32_t)red << 8) | blue;
        uint16_t byteIndex = 0;
        
        for (int i = 23; i >= 0; --i) {
            bool isBitSet = (colorPattern >> i) & 0x01;
            // Упаковка в 3-бітові шаблони високих/низьких рівнів для SPI TX
            targetBuffer[byteIndex++] = isBitSet ? 0b110 : 0b100;
        }
    }
};
