#include <stdint.h>
#include <stdbool.h>

// Структура калібрувальних коефіцієнтів BMP280
typedef struct {
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
} bmp280_calib_param_t;

// Розпакування 24-байтного масиву NVM регістрів 0x88..0x9E
void bmp280_parse_calib_params(const uint8_t *reg_data, bmp280_calib_param_t *calib) {
    calib->dig_T1 = (uint16_t)((reg_data[1] << 8) | reg_data[0]);
    calib->dig_T2 = (int16_t)((reg_data[3] << 8) | reg_data[2]);
    calib->dig_T3 = (int16_t)((reg_data[5] << 8) | reg_data[4]);

    calib->dig_P1 = (uint16_t)((reg_data[7] << 8) | reg_data[6]);
    calib->dig_P2 = (int16_t)((reg_data[9] << 8) | reg_data[8]);
    calib->dig_P3 = (int16_t)((reg_data[11] << 8) | reg_data[10]);
    calib->dig_P4 = (int16_t)((reg_data[13] << 8) | reg_data[12]);
    calib->dig_P5 = (int16_t)((reg_data[15] << 8) | reg_data[14]);
    calib->dig_P6 = (int16_t)((reg_data[17] << 8) | reg_data[16]);
    calib->dig_P7 = (int16_t)((reg_data[19] << 8) | reg_data[18]);
    calib->dig_P8 = (int16_t)((reg_data[21] << 8) | reg_data[20]);
    calib->dig_P9 = (int16_t)((reg_data[23] << 8) | reg_data[22]);
}

// Розпакування 20-бітового значення з 3 байтів регістрів (MSB, LSB, XLSB)
int32_t bmp280_parse_adc_20bit(const uint8_t *raw_bytes) {
    uint32_t msb  = (uint32_t)raw_bytes[0];
    uint32_t lsb  = (uint32_t)raw_bytes[1];
    uint32_t xlsb = (uint32_t)raw_bytes[2];
    return (int32_t)((msb << 12) | (lsb << 4) | (xlsb >> 4));
}
