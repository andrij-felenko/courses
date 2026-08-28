// bsp/bsp_bme280.h
#ifndef BSP_BME280_H
#define BSP_BME280_H

#include "hal/hal_i2c.h"

// Непрозорий дескриптор пристрою (Opaque Pointer)
typedef struct bsp_bme280_dev bsp_bme280_t;

typedef struct {
    float temperature_c;
    float humidity_percent;
    float pressure_hpa;
} bsp_bme280_data_t;

// Статичне виділення пам'яті під дескриптор (без виклику malloc)
typedef struct bsp_bme280_storage {
    uint8_t internal_bytes[64];
} bsp_bme280_storage_t;

bsp_bme280_t* bsp_bme280_init(bsp_bme280_storage_t* storage, hal_i2c_bus_t* bus, uint8_t i2c_addr);
bool bsp_bme280_read(bsp_bme280_t* dev, bsp_bme280_data_t* out_data);

#endif // BSP_BME280_H
