#include <Arduino.h>

struct Bmp280CalibData {
    uint16_t dig_T1;
    int16_t  dig_T2;
    int16_t  dig_T3;
    uint16_t dig_P1;
    int16_t  dig_P2;
    int16_t  dig_P3;
    int16_t  dig_P4;
    int16_t  dig_P5;
    int16_t  dig_P6;
    int16_t  dig_P7;
    int16_t  dig_P8;
    int16_t  dig_P9;

    void parseNvmBuffer(const uint8_t buffer[24]) {
        dig_T1 = static_cast<uint16_t>((buffer[1] << 8) | buffer[0]);
        dig_T2 = static_cast<int16_t>((buffer[3] << 8) | buffer[2]);
        dig_T3 = static_cast<int16_t>((buffer[5] << 8) | buffer[4]);

        dig_P1 = static_cast<uint16_t>((buffer[7] << 8) | buffer[6]);
        dig_P2 = static_cast<int16_t>((buffer[9] << 8) | buffer[8]);
        dig_P3 = static_cast<int16_t>((buffer[11] << 8) | buffer[10]);
        dig_P4 = static_cast<int16_t>((buffer[13] << 8) | buffer[12]);
        dig_P5 = static_cast<int16_t>((buffer[15] << 8) | buffer[14]);
        dig_P6 = static_cast<int16_t>((buffer[17] << 8) | buffer[16]);
        dig_P7 = static_cast<int16_t>((buffer[19] << 8) | buffer[18]);
        dig_P8 = static_cast<int16_t>((buffer[21] << 8) | buffer[20]);
        dig_P9 = static_cast<int16_t>((buffer[23] << 8) | buffer[22]);
    }

    static int32_t unpackAdc20Bit(uint8_t msb, uint8_t lsb, uint8_t xlsb) {
        return static_cast<int32_t>((static_cast<uint32_t>(msb) << 12) |
                                    (static_cast<uint32_t>(lsb) << 4) |
                                    (static_cast<uint32_t>(xlsb) >> 4));
    }
};
