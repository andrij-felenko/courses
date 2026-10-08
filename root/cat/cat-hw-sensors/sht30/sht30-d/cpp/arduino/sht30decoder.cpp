#include <Arduino.h>

class SHT30Decoder {
public:
    // Обчислення CRC-8 з поліномом 0x31 та початковим значенням 0xFF
    static uint8_t calculateCRC8(const uint8_t* data, uint8_t length) {
        uint8_t crc = 0xFF;
        for (uint8_t i = 0; i < length; i++) {
            crc ^= data[i];
            for (uint8_t bit = 8; bit > 0; --bit) {
                if (crc & 0x80) {
                    crc = (crc << 1) ^ 0x31;
                } else {
                    crc = (crc << 1);
                }
            }
        }
        return crc;
    }

    // Декодування сирого 6-байтового пакета з перевіркою CRC
    static bool parse(const uint8_t buffer[6], float& tempC, float& humidityRH) {
        if (calculateCRC8(&buffer[0], 2) != buffer[2]) {
            return false; // Помилка CRC температури
        }
        if (calculateCRC8(&buffer[3], 2) != buffer[5]) {
            return false; // Помилка CRC вологості
        }

        uint16_t st = (static_cast<uint16_t>(buffer[0]) << 8) | buffer[1];
        uint16_t srh = (static_cast<uint16_t>(buffer[3]) << 8) | buffer[4];

        tempC = -45.0f + 175.0f * (static_cast<float>(st) / 65535.0f);
        humidityRH = 100.0f * (static_cast<float>(srh) / 65535.0f);

        return true;
    }
};
