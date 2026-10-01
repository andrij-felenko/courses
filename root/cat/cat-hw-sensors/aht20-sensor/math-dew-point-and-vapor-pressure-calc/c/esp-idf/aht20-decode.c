#include <stdint.h>

typedef struct {
    float humidity;
    float temperature;
} aht20_reading_t;

aht20_reading_t aht20_decode(const uint8_t raw[6]) {
    uint32_t s_rh = ((uint32_t)raw[1] << 12) | ((uint32_t)raw[2] << 4) | ((uint32_t)raw[3] >> 4);
    uint32_t s_t  = (((uint32_t)raw[3] & 0x0F) << 16) | ((uint32_t)raw[4] << 8) | (uint32_t)raw[5];

    aht20_reading_t res;
    res.humidity = ((float)s_rh / 1048576.0f) * 100.0f;
    res.temperature = ((float)s_t / 1048576.0f) * 200.0f - 50.0f;
    return res;
}
