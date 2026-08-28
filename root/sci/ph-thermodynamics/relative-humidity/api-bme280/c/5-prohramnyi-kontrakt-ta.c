#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

typedef struct {
    uint16_t dig_T1;
    int16_t  dig_T2;
    int16_t  dig_T3;
    uint8_t  dig_H1;
    int16_t  dig_H2;
    uint8_t  dig_H3;
    int16_t  dig_H4;
    int16_t  dig_H5;
    int8_t   dig_H6;
} bme280_calib_t;

typedef struct {
    uint8_t i2c_addr;
    bme280_calib_t calib;
} bme280_handle_t;

static bool platform_i2c_read(uint8_t addr, uint8_t reg, uint8_t *data, uint16_t len) {
    for (uint16_t i = 0; i < len; i++) data[i] = 0x80;
    if (len == 1 && reg == 0xD0) data[0] = 0x60;
    return true;
}

static bool platform_i2c_write(uint8_t addr, uint8_t reg, uint8_t val) {
    return true;
}

int bme280_init(bme280_handle_t *dev, uint8_t i2c_addr) {
    if (!dev) return -1;
    dev->i2c_addr = i2c_addr;

    uint8_t id = 0;
    platform_i2c_read(dev->i2c_addr, 0xD0, &id, 1);
    if (id != 0x60) return -2;

    dev->calib.dig_T1 = 27504;
    dev->calib.dig_T2 = 26435;
    dev->calib.dig_T3 = -1000;
    dev->calib.dig_H1 = 75;
    dev->calib.dig_H2 = 360;
    dev->calib.dig_H3 = 0;
    dev->calib.dig_H4 = 300;
    dev->calib.dig_H5 = 50;
    dev->calib.dig_H6 = 30;

    platform_i2c_write(dev->i2c_addr, 0xF2, 0x01);
    platform_i2c_write(dev->i2c_addr, 0xF4, 0x27);

    return 0;
}

int bme280_read_measurements(const bme280_handle_t *dev, double *out_temp, double *out_humidity) {
    uint8_t buf[8];
    if (!platform_i2c_read(dev->i2c_addr, 0xF7, buf, 8)) return -1;

    int32_t adc_T = (buf[3] << 12) | (buf[4] << 4) | (buf[5] >> 4);
    int32_t adc_H = (buf[6] << 8) | buf[7];

    int32_t var1_t = ((((adc_T >> 3) - ((int32_t)dev->calib.dig_T1 << 1))) * ((int32_t)dev->calib.dig_T2)) >> 11;
    int32_t var2_t = (((((adc_T >> 4) - ((int32_t)dev->calib.dig_T1)) * ((adc_T >> 4) - ((int32_t)dev->calib.dig_T1))) >> 12) * ((int32_t)dev->calib.dig_T3)) >> 14;
    int32_t t_fine = var1_t + var2_t;

    if (out_temp) {
        *out_temp = ((t_fine * 5 + 128) >> 8) / 100.0;
    }

    if (out_humidity) {
        int32_t v_x1 = (t_fine - ((int32_t)76800));
        v_x1 = (((((adc_H << 14) - (((int32_t)dev->calib.dig_H4) << 20) - (((int32_t)dev->calib.dig_H5) * v_x1)) + 16384) >> 15) *
                (((((((v_x1 * ((int32_t)dev->calib.dig_H6)) >> 10) * (((v_x1 * ((int32_t)dev->calib.dig_H3)) >> 11) + 32768)) >> 10) + 2097152) *
                  ((int32_t)dev->calib.dig_H2) + 8192) >> 14));
        v_x1 = (v_x1 - (((((v_x1 >> 15) * (v_x1 >> 15)) >> 7) * ((int32_t)dev->calib.dig_H1)) >> 4));
        if (v_x1 < 0) v_x1 = 0;
        if (v_x1 > 419430400) v_x1 = 419430400;
        *out_humidity = (v_x1 >> 12) / 1024.0;
    }

    return 0;
}

int main(void) {
    bme280_handle_t dev;
    if (bme280_init(&dev, 0x76) == 0) {
        double temp = 0.0, hum = 0.0;
        if (bme280_read_measurements(&dev, &temp, &hum) == 0) {
            printf("BME280 C Driver: T = %.2f C, RH = %.2f %%\n", temp, hum);
        }
    }
    return 0;
}
