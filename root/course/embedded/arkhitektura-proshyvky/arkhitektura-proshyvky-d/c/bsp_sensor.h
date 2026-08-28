// bsp_sensor.h — Публічний заголовок: чистий інтерфейс для шарів вище
#ifndef BSP_SENSOR_H
#define BSP_SENSOR_H

#include <stdbool.h>
#include <stdint.h>

// Неповний тип: клієнтський код не знає розміру й полів структури
typedef struct bsp_sensor_handle bsp_sensor_t;

typedef struct {
    float temperature_c;
    float pressure_kpa;
} bsp_sensor_data_t;

// Функції життєвого циклу
bsp_sensor_t* bsp_sensor_create(uint8_t bus_id, uint8_t i2c_address);
bool bsp_sensor_read_data(bsp_sensor_t* dev, bsp_sensor_data_t* out_data);
void bsp_sensor_destroy(bsp_sensor_t* dev);

#endif // BSP_SENSOR_H
