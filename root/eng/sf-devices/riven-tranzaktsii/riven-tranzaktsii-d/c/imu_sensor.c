/**
 * @file imu_sensor.c
 * @brief Алгоритмічний драйвер сенсора на C99.
 */

#include "bus_transaction_c99.h"

#define REG_CHIP_ID      0x00
#define REG_PWR_MGMT_1   0x06
#define REG_ACCEL_CONFIG 0x14
#define REG_ACCEL_XOUT_H 0x1F

#define EXPECTED_CHIP_ID 0x42

typedef struct {
    float x;
    float y;
    float z;
} vec3_t;

typedef struct {
    const bus_interface_t *bus;
    float                  accel_scale;
    bool                   is_ready;
} imu_driver_t;

bus_status_t imu_init(imu_driver_t *dev, const bus_interface_t *bus) {
    if (!dev || !bus) return BUS_STATUS_ERR_PARAM;
    dev->bus      = bus;
    dev->is_ready = false;

    /* 1. Перевірка ідентифікатора кристала */
    uint8_t id = 0;
    bus_status_t st = bus_read_u8(dev->bus, REG_CHIP_ID, &id);
    if (st != BUS_STATUS_OK) return st;
    if (id != EXPECTED_CHIP_ID) return BUS_STATUS_ERR_IO;

    /* 2. Пробудження датчика (скидання біта SLEEP у 0) */
    st = bus_write_u8(dev->bus, REG_PWR_MGMT_1, 0x01);
    if (st != BUS_STATUS_OK) return st;

    /* 3. Налаштування діапазону ±4g (масштаб 4.0 * 9.80665 / 32768.0) */
    st = bus_write_u8(dev->bus, REG_ACCEL_CONFIG, 0x08);
    if (st != BUS_STATUS_OK) return st;

    dev->accel_scale = (4.0f * 9.80665f) / 32768.0f;
    dev->is_ready    = true;
    return BUS_STATUS_OK;
}

bus_status_t imu_read_accel(imu_driver_t *dev, vec3_t *out_accel) {
    if (!dev || !dev->is_ready || !out_accel) return BUS_STATUS_ERR_PARAM;

    /* Пакетне зчитування 6 послідовних байтів: X_H, X_L, Y_H, Y_L, Z_H, Z_L */
    uint8_t raw[6];
    bus_status_t st = bus_read_reg(dev->bus, REG_ACCEL_XOUT_H, raw, sizeof(raw));
    if (st != BUS_STATUS_OK) return st;

    /* Розпакування 16-бітних знакових величин (Big Endian) */
    int16_t raw_x = (int16_t)(((uint16_t)raw[0] << 8) | raw[1]);
    int16_t raw_y = (int16_t)(((uint16_t)raw[2] << 8) | raw[3]);
    int16_t raw_z = (int16_t)(((uint16_t)raw[4] << 8) | raw[5]);

    out_accel->x = (float)raw_x * dev->accel_scale;
    out_accel->y = (float)raw_y * dev->accel_scale;
    out_accel->z = (float)raw_z * dev->accel_scale;

    return BUS_STATUS_OK;
}
