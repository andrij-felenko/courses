#include <Arduino.h>

struct AHT20RawData {
    uint32_t s_rh;
    uint32_t s_t;
};

AHT20RawData unpackAHT20(const uint8_t raw[6]) {
    AHT20RawData data;
    
    // Явне приведення типів до uint32_t запобігає втраті бітів при зсуві
    data.s_rh = ((uint32_t)raw[1] << 12) | 
                ((uint32_t)raw[2] << 4)  | 
                ((uint32_t)raw[3] >> 4);

    data.s_t = (((uint32_t)raw[3] & 0x0F) << 16) | 
               ((uint32_t)raw[4] << 8)         | 
               (uint32_t)raw[5];

    return data;
}
