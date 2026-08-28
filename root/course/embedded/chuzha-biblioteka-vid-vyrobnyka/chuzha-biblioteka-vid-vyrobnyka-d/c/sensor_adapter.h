/* =================== Файл: sensor_adapter.h =================== */
#ifndef SENSOR_ADAPTER_H
#define SENSOR_ADAPTER_H

#include <stdint.h>
#include <stdbool.h>

/* Системний результат без прив'язки до вендорських заголовків */
typedef struct {
    int32_t temperature_centi_c; /* 2550 = 25.50 °C */
    uint32_t pressure_pa;        /* 101325 Па */
} sys_env_sample_t;

typedef enum {
    SYS_SENSOR_OK = 0,
    SYS_SENSOR_ERR_COMM,
    SYS_SENSOR_ERR_NOT_FOUND,
    SYS_SENSOR_ERR_INVALID_PARAM
} sys_sensor_status_t;

/* Непрозорий дескриптор адаптера */
typedef struct sensor_adapter sensor_adapter_t;

/* Інтерфейс системної шини */
typedef struct {
    bool (*read)(void *bus_ctx, uint8_t dev_addr, uint8_t reg, uint8_t *buf, uint16_t len);
    bool (*write)(void *bus_ctx, uint8_t dev_addr, uint8_t reg, const uint8_t *buf, uint16_t len);
    void *bus_ctx;
} sys_bus_interface_t;

/* Оголошення функцій адаптера */
sensor_adapter_t* sensor_adapter_create(const sys_bus_interface_t *bus, uint8_t i2c_addr);
sys_sensor_status_t sensor_adapter_init(sensor_adapter_t *adapter);
sys_sensor_status_t sensor_adapter_read_data(sensor_adapter_t *adapter, sys_env_sample_t *out_sample);
void sensor_adapter_destroy(sensor_adapter_t *adapter);

#endif /* SENSOR_ADAPTER_H */

/* =================== Файл: sensor_adapter.c =================== */
#include "sensor_adapter.h"
#include <stdlib.h>

/* Вендорський заголовок підключається ВИКЛЮЧНО тут */
#include "bme280.h" 

struct sensor_adapter {
    struct bme280_dev dev;
    sys_bus_interface_t bus;
    uint8_t i2c_addr;
};

/* Статичні містки для виклику системної шини */
static int8_t c_bus_read(uint8_t reg_addr, uint8_t *data, uint32_t len, void *intf_ptr) {
    sensor_adapter_t *self = (sensor_adapter_t*)intf_ptr;
    if (!self || !data) return BME280_E_NULL_PTR;
    bool ok = self->bus.read(self->bus.bus_ctx, self->i2c_addr, reg_addr, data, (uint16_t)len);
    return ok ? BME280_OK : BME280_E_COMM_FAIL;
}

static int8_t c_bus_write(uint8_t reg_addr, const uint8_t *data, uint32_t len, void *intf_ptr) {
    sensor_adapter_t *self = (sensor_adapter_t*)intf_ptr;
    if (!self || !data) return BME280_E_NULL_PTR;
    bool ok = self->bus.write(self->bus.bus_ctx, self->i2c_addr, reg_addr, data, (uint16_t)len);
    return ok ? BME280_OK : BME280_E_COMM_FAIL;
}

static void c_bus_delay_us(uint32_t period_us, void *intf_ptr) {
    (void)intf_ptr;
    /* У реальній системі: виклик системної затримки */
}

sys_sensor_status_t sensor_adapter_init(sensor_adapter_t *adapter) {
    if (!adapter) return SYS_SENSOR_ERR_INVALID_PARAM;
    
    adapter->dev.intf_ptr = adapter;
    adapter->dev.read = c_bus_read;
    adapter->dev.write = c_bus_write;
    adapter->dev.delay_us = c_bus_delay_us;
    adapter->dev.intf = BME280_I2C_INTF;

    int8_t rslt = bme280_init(&adapter->dev);
    if (rslt == BME280_E_DEV_NOT_FOUND) return SYS_SENSOR_ERR_NOT_FOUND;
    if (rslt != BME280_OK) return SYS_SENSOR_ERR_COMM;

    /* Конфігурація режиму роботи сенсора */
    struct bme280_settings settings;
    settings.osr_h = BME280_OVERSAMPLING_1X;
    settings.osr_p = BME280_OVERSAMPLING_16X;
    settings.osr_t = BME280_OVERSAMPLING_2X;
    settings.filter = BME280_FILTER_COEFF_16;
    bme280_set_sensor_settings(BME280_SEL_ALL_SETTINGS, &settings, &adapter->dev);
    bme280_set_sensor_mode(BME280_POWERMODE_NORMAL, &adapter->dev);

    return SYS_SENSOR_OK;
}

sys_sensor_status_t sensor_adapter_read_data(sensor_adapter_t *adapter, sys_env_sample_t *out_sample) {
    if (!adapter || !out_sample) return SYS_SENSOR_ERR_INVALID_PARAM;
    
    struct bme280_data comp_data;
    int8_t rslt = bme280_get_sensor_data(BME280_ALL, &comp_data, &adapter->dev);
    if (rslt != BME280_OK) return SYS_SENSOR_ERR_COMM;

    out_sample->temperature_centi_c = (int32_t)(comp_data.temperature * 100.0f);
    out_sample->pressure_pa = (uint32_t)comp_data.pressure;
    return SYS_SENSOR_OK;
}
