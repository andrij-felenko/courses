// bsp_sensor.c — Приватна реалізація, прихована від застосунку
#include "bsp_sensor.h"
#include <stdlib.h>

struct bsp_sensor_handle {
    uint8_t bus_id;
    uint8_t address;
    int16_t calib_t1;
    int16_t calib_t2;
    uint32_t last_poll_timestamp;
};

bsp_sensor_t* bsp_sensor_create(uint8_t bus_id, uint8_t i2c_address) {
    bsp_sensor_t* dev = (bsp_sensor_t*)malloc(sizeof(bsp_sensor_t));
    if (!dev) return NULL;
    dev->bus_id = bus_id;
    dev->address = i2c_address;
    dev->calib_t1 = 0;
    dev->calib_t2 = 0;
    dev->last_poll_timestamp = 0;
    return dev;
}

bool bsp_sensor_read_data(bsp_sensor_t* dev, bsp_sensor_data_t* out_data) {
    if (!dev || !out_data) return false;
    // Логіка зчитування через HAL-шину з використанням dev->bus_id
    out_data->temperature_c = 24.5f;
    out_data->pressure_kpa = 101.3f;
    return true;
}

void bsp_sensor_destroy(bsp_sensor_t* dev) {
    if (dev) {
        free(dev);
    }
}
