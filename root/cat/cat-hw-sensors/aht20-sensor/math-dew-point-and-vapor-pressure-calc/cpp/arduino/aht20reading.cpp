#include <stdint.h>

struct AHT20Reading {
    float humidity;
    float temperature;
};

AHT20Reading decodeAHT20(const uint8_t raw[6]) {
    uint32_t sRh = (static_cast<uint32_t>(raw[1]) << 12) |
                   (static_cast<uint32_t>(raw[2]) << 4)  |
                   (static_cast<uint32_t>(raw[3]) >> 4);

    uint32_t sT  = ((static_cast<uint32_t>(raw[3]) & 0x0F) << 16) |
                   (static_cast<uint32_t>(raw[4]) << 8)         |
                   static_cast<uint32_t>(raw[5]);

    return {
        (static_cast<float>(sRh) / 1048576.0f) * 100.0f,
        (static_cast<float>(sT) / 1048576.0f) * 200.0f - 50.0f
    };
}
