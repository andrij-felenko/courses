#include "driver/i2c.h"
#include "esp_err.h"

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
} bme280_calib_t;

static bme280_calib_t g_calib;
static int32_t g_t_fine = 0;

esp_err_t bme280_read_calib(i2c_port_t port, uint8_t addr) {
    uint8_t reg = 0x88;
    uint8_t data[24];
    esp_err_t ret = i2c_master_write_read_device(port, addr, &reg, 1, data, 24, 1000 / portTICK_PERIOD_MS);
    if (ret != ESP_OK) return ret;

    g_calib.dig_T1 = data[0]  | (data[1]  << 8);
    g_calib.dig_T2 = data[2]  | (data[3]  << 8);
    g_calib.dig_T3 = data[4]  | (data[5]  << 8);
    g_calib.dig_P1 = data[6]  | (data[7]  << 8);
    g_calib.dig_P2 = data[8]  | (data[9]  << 8);
    g_calib.dig_P3 = data[10] | (data[11] << 8);
    g_calib.dig_P4 = data[12] | (data[13] << 8);
    g_calib.dig_P5 = data[14] | (data[15] << 8);
    g_calib.dig_P6 = data[16] | (data[17] << 8);
    g_calib.dig_P7 = data[18] | (data[19] << 8);
    g_calib.dig_P8 = data[20] | (data[21] << 8);
    g_calib.dig_P9 = data[22] | (data[23] << 8);
    return ESP_OK;
}

int32_t bme280_calc_temp(int32_t adc_T) {
    int32_t var1 = (((adc_T >> 3) - ((int32_t)g_calib.dig_T1 << 1)) * (int32_t)g_calib.dig_T2) >> 11;
    int32_t var2 = (((((adc_T >> 4) - (int32_t)g_calib.dig_T1) * ((adc_T >> 4) - (int32_t)g_calib.dig_T1)) >> 12) * (int32_t)g_calib.dig_T3) >> 14;
    g_t_fine = var1 + var2;
    return (g_t_fine * 5 + 128) >> 8;
}
