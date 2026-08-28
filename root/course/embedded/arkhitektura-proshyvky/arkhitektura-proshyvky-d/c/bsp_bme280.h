// bsp/bsp_bme280.h
#ifndef BSP_BME280_H
#define BSP_BME280_H

#include "hal/hal_i2c.h"

typedef struct bsp_bme280_dev bsp_bme280_t;

typedef struct {
    uint8_t memory_pool[48]; // Статичний буфер для дескриптора
} bsp_bme280_storage_t;

typedef struct {
    float temperature_c;
    float humidity_rh;
    float pressure_hpa;
} bsp_bme280_readings_t;

bsp_bme280_t* bsp_bme280_init(bsp_bme280_storage_t* storage, 
                              const hal_i2c_bus_t* bus, 
                              uint8_t i2c_addr);

bool bsp_bme280_measure(bsp_bme280_t* dev, bsp_bme280_readings_t* out_readings);

#endif // BSP_BME280_H
