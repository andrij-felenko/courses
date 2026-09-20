#include <Arduino.h>

class BcdThumbwheelReader {
private:
    uint8_t pl_pin, cp_pin, q7_pin;

public:
    BcdThumbwheelReader(uint8_t pl, uint8_t cp, uint8_t q7) 
        : pl_pin(pl), cp_pin(cp), q7_pin(q7) {}

    void begin() {
        pinMode(pl_pin, OUTPUT);
        pinMode(cp_pin, OUTPUT);
        pinMode(q7_pin, INPUT);
        digitalWrite(pl_pin, HIGH);
        digitalWrite(cp_pin, LOW);
    }

    bool readAsUint32(uint8_t byteCount, uint32_t &outValue) {
        digitalWrite(pl_pin, LOW);
        delayMicroseconds(1);
        digitalWrite(pl_pin, HIGH);

        outValue = 0;
        uint32_t mult = 1;

        for (uint8_t i = 0; i < byteCount; i++) {
            uint8_t raw = shiftIn(q7_pin, cp_pin, MSBFIRST);
            uint8_t data = ~raw; // Інверсія pull-up

            uint8_t low_n = data & 0x0F;
            uint8_t high_n = (data >> 4) & 0x0F;

            if (low_n > 9 || high_n > 9) return false;

            outValue += low_n * mult;
            mult *= 10;
            outValue += high_n * mult;
            mult *= 10;
        }
        return true;
    }
};
