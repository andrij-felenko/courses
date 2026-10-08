#include <Arduino.h>

class AS5048Parser {
public:
    static bool calculateEvenParity(uint16_t value) {
        uint16_t count = 0;
        for (uint8_t i = 0; i < 16; i++) {
            if ((value >> i) & 0x01) count++;
        }
        return (count % 2) == 0;
    }

    static bool processFrame(uint16_t rxFrame, uint16_t &angle, bool &hasError) {
        if (!calculateEvenParity(rxFrame)) {
            return false; // Помилка парності
        }
        hasError = (rxFrame & 0x4000) != 0;
        angle = rxFrame & 0x3FFF;
        return true;
    }
};
