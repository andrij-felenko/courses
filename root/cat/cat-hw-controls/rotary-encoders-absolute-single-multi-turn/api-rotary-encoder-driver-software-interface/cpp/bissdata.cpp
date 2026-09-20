#include <Arduino.h>

struct BissData {
    uint32_t position;
    bool error;
    bool warning;
    bool valid;
};

class BissEncoderDriver {
private:
    uint8_t sckPin;
    uint8_t misoPin;
    uint8_t dataBits;

    uint8_t calcCrc6(uint64_t payload, uint8_t len) {
        uint8_t crc = 0;
        for (int8_t i = len - 1; i >= 0; i--) {
            uint8_t bit = (payload >> i) & 1;
            uint8_t msb = (crc >> 5) & 1;
            crc = (crc << 1) & 0x3F;
            if (bit ^ msb) crc ^= 0x03;
        }
        return crc ^ 0x3F;
    }

public:
    BissEncoderDriver(uint8_t sck, uint8_t miso, uint8_t bits = 24) 
        : sckPin(sck), misoPin(miso), dataBits(bits) {}

    void begin() {
        pinMode(sckPin, OUTPUT);
        pinMode(misoPin, INPUT);
        digitalWrite(sckPin, HIGH);
    }

    BissData read() {
        BissData result = {0, false, false, false};
        uint64_t raw = 0;
        
        // Тактування та читання бітів
        for (uint8_t i = 0; i < dataBits + 8; i++) {
            digitalWrite(sckPin, LOW);
            delayMicroseconds(1);
            digitalWrite(sckPin, HIGH);
            delayMicroseconds(1);
            raw = (raw << 1) | digitalRead(misoPin);
        }

        uint8_t recCrc = raw & 0x3F;
        uint64_t payload = raw >> 6;
        uint8_t expCrc = calcCrc6(payload, dataBits + 2);

        if (recCrc != expCrc) return result;

        result.warning = ((payload & 1) == 0);
        result.error = (((payload >> 1) & 1) == 0);
        
        uint32_t gray = (payload >> 2) & ((1UL << dataBits) - 1);
        uint32_t bin = gray;
        for (uint32_t mask = bin >> 1; mask > 0; mask >>= 1) {
            bin ^= mask;
        }
        result.position = bin;
        result.valid = !result.error;
        return result;
    }
};
