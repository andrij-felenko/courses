#include <Wire.h>

class AHT20Sensor {
public:
    static const uint8_t ADDR = 0x38;

    static uint8_t calculateCRC8(const uint8_t *buffer, size_t size) {
        uint8_t crc = 0xFF;
        for (size_t i = 0; i < size; ++i) {
            crc ^= buffer[i];
            for (uint8_t b = 0; b < 8; ++b) {
                crc = (crc & 0x80) ? (uint8_t)((crc << 1) ^ 0x31) : (uint8_t)(crc << 1);
            }
        }
        return crc;
    }

    bool fetchMeasurement(uint32_t &rawRH, uint32_t &rawT) {
        Wire.beginTransmission(ADDR);
        Wire.write(0xAC);
        Wire.write(0x33);
        Wire.write(0x00);
        if (Wire.endTransmission() != 0) return false;

        delay(80);

        if (Wire.requestFrom(ADDR, (uint8_t)7) != 7) return false;

        uint8_t data[7];
        for (uint8_t i = 0; i < 7; ++i) {
            data[i] = Wire.read();
        }

        if ((data[0] & 0x80) != 0 || (data[0] & 0x08) == 0) return false;
        if (calculateCRC8(data, 6) != data[6]) return false;

        rawRH = ((uint32_t)data[1] << 12) | ((uint32_t)data[2] << 4) | ((uint32_t)data[3] >> 4);
        rawT  = (((uint32_t)data[3] & 0x0F) << 16) | ((uint32_t)data[4] << 8) | (uint32_t)data[5];

        return true;
    }
};
