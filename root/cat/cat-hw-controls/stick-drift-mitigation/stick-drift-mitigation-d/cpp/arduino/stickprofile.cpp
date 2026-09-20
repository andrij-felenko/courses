#include <Arduino.h>

struct StickProfile {
    uint32_t magic = 0x43414C49;
    uint8_t version = 1;
    uint16_t x_zero = 2048;
    uint16_t y_zero = 2048;
    float x_scale_neg = 1.0f / 2048.0f;
    float x_scale_pos = 1.0f / 2047.0f;
    float y_scale_neg = 1.0f / 2048.0f;
    float y_scale_pos = 1.0f / 2047.0f;
    uint16_t crc16 = 0;
};

class ProfileManager {
public:
    static uint16_t computeCRC16(const uint8_t* data, size_t len) {
        uint16_t crc = 0xFFFF;
        for (size_t i = 0; i < len; ++i) {
            crc ^= static_cast<uint16_t>(data[i]) << 8;
            for (uint8_t bit = 0; bit < 8; ++bit) {
                if (crc & 0x8000) {
                    crc = (crc << 1) ^ 0x1021;
                } else {
                    crc <<= 1;
                }
            }
        }
        return crc;
    }

    static bool verifyAndLoad(const uint8_t* buffer, StickProfile& profile) {
        memcpy(&profile, buffer, sizeof(StickProfile));

        if (profile.magic != 0x43414C49) {
            return false;
        }

        size_t payload_len = sizeof(StickProfile) - sizeof(uint16_t);
        uint16_t expected_crc = computeCRC16(reinterpret_cast<const uint8_t*>(&profile), payload_len);

        if (profile.crc16 != expected_crc) {
            // Аварійний запуск фабричного профілю
            profile = StickProfile(); // Скидання до конструктора за замовчуванням
            return false;
        }
        return true;
    }
};
