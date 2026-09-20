#include <Arduino.h>

struct AppConfig {
    uint8_t deviceAddress;
    uint8_t baudRateId;
    bool dhcpEnabled;
    bool parityCheck;

    static AppConfig fromRawByte(uint8_t rawByte) {
        uint8_t val = ~rawByte; // Інверсія active-LOW підтяжки
        return AppConfig {
            .deviceAddress = static_cast<uint8_t>(val & 0x07),
            .baudRateId   = static_cast<uint8_t>((val >> 3) & 0x03),
            .dhcpEnabled  = static_cast<bool>((val >> 5) & 0x01),
            .parityCheck  = static_cast<bool>((val >> 6) & 0x01)
        };
    }
};
