#include <Arduino.h>

class AHT20CRC {
public:
    // Обчислення CRC8 для буфера даних AHT20 (поліном 0x31, початковий стан 0xFF)
    static uint8_t calculateCRC8(const uint8_t* data, size_t length) {
        uint8_t crc = 0xFF;
        for (size_t i = 0; i < length; i++) {
            crc ^= data[i];
            for (uint8_t bit = 0; bit < 8; bit++) {
                if (crc & 0x80) {
                    crc = (uint8_t)((crc << 1) ^ 0x31);
                } else {
                    crc = (uint8_t)(crc << 1);
                }
            }
        }
        return crc;
    }

    // Розбір кадру даних із перевіркою контрольної суми
    static bool parseFrame(const uint8_t buffer[7], float &humidity, float &temperature) {
        uint8_t expectedCRC = calculateCRC8(buffer, 6);
        if (expectedCRC != buffer[6]) {
            Serial.print(F("CRC8 mismatch! Computed: 0x"));
            Serial.print(expectedCRC, HEX);
            Serial.print(F(", expected: 0x"));
            Serial.println(buffer[6], HEX);
            return false;
        }

        uint32_t rawHumidity = ((uint32_t)buffer[1] << 12) | ((uint32_t)buffer[2] << 4) | ((uint32_t)buffer[3] >> 4);
        humidity = ((float)rawHumidity / 1048576.0f) * 100.0f;

        uint32_t rawTemp = (((uint32_t)buffer[3] & 0x0F) << 16) | ((uint32_t)buffer[4] << 8) | (uint32_t)buffer[5];
        temperature = ((float)rawTemp / 1048576.0f) * 200.0f - 50.0f;

        return true;
    }
};
