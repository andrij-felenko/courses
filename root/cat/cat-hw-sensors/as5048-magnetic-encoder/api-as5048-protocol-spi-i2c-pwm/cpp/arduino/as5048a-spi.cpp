#include <SPI.h>

class AS5048A_SPI {
private:
    uint8_t csPin;

    bool checkParity(uint16_t data) {
        uint16_t count = 0;
        for (int i = 0; i < 16; i++) {
            if ((data >> i) & 1) count++;
        }
        return (count % 2) == 0;
    }

    uint16_t transfer16(uint16_t command) {
        digitalWrite(csPin, LOW);
        uint16_t response = SPI.transfer16(command);
        digitalWrite(csPin, HIGH);
        return response;
    }

public:
    AS5048A_SPI(uint8_t cs) : csPin(cs) {}

    void begin() {
        pinMode(csPin, OUTPUT);
        digitalWrite(csPin, HIGH);
        SPI.begin();
    }

    bool readAngle(float &angleDeg) {
        SPI.beginTransaction(SPISettings(1000000, MSBFIRST, SPI_MODE1));
        
        // Крок 1: Запит регістру кута (0xFFFF)
        transfer16(0xFFFF);
        
        // Крок 2: Виштовхування результату командою NOP (0x0000)
        uint16_t rawFrame = transfer16(0x0000);
        
        SPI.endTransaction();

        // Валідація контрольної суми парності
        if (!checkParity(rawFrame)) return false;

        // Перевірка прапорця помилки EF (біт 14)
        if (rawFrame & 0x4000) return false;

        uint16_t rawAngle = rawFrame & 0x3FFF;
        angleDeg = (float)rawAngle * 360.0f / 16384.0f;
        return true;
    }
};
