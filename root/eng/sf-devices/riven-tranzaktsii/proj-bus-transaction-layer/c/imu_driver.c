/**
 * @file imu_driver.c
 * @brief Реалізація логіки драйвера IMU без прив'язки до фізичної шини.
 */

#include "imu_driver.h"

/* Стандартне гравітаційне прискорення для переводу g у м/с² */
#define GRAVITY_EARTH 9.80665f
#define PI_CONST      3.14159265358979323846f

bus_status_t imu_init(imu_sensor_t *dev, const bus_interface_t *bus) {
    if (!dev || !bus) return BUS_ERR_INVALID_ARG;

    dev->bus         = bus;
    dev->initialized = false;

    /* 1. Зчитування ідентифікатора кристала (Chip ID / WHO_AM_I) */
    uint8_t chip_id = 0;
    bus_status_t status = bus_read_u8(dev->bus, IMU_REG_CHIP_ID, &chip_id);
    if (status != BUS_OK) {
        return status;
    }

    if (chip_id != IMU_EXPECTED_CHIP_ID) {
        return BUS_ERR_IO; /* Невідомий чіп або апаратна помилка ліній зв'язку */
    }

    /* 2. Переведення сенсора в активний режим живлення (Power Control) */
    status = bus_write_u8(dev->bus, IMU_REG_PWR_CTRL, 0x0E); /* Увімкнути Accel, Gyro та температурний сенсор */
    if (status != BUS_OK) {
        return status;
    }

    /* 3. Конфігурація акселерометра: діапазон ±4g, частота видачі ODR = 100 Гц */
    status = bus_write_u8(dev->bus, IMU_REG_ACC_CONF, 0xA8);
    if (status != BUS_OK) {
        return status;
    }

    /* 4. Конфігурація гіроскопа: діапазон ±2000 dps, ODR = 100 Гц */
    status = bus_write_u8(dev->bus, IMU_REG_GYR_CONF, 0xA9);
    if (status != BUS_OK) {
        return status;
    }

    /* Розрахунок масштабних коефіцієнтів у системі SI:
     * Для ±4g при 16-бітному знаковому форматі: 4.0 * 9.80665 / 32768.0 LSB
     * Для ±2000 dps: 2000.0 * (PI / 180.0) / 32768.0 LSB */
    dev->accel_scale  = (4.0f * GRAVITY_EARTH) / 32768.0f;
    dev->gyro_scale   = (2000.0f * (PI_CONST / 180.0f)) / 32768.0f;
    dev->initialized  = true;

    return BUS_OK;
}

bus_status_t imu_read_all(imu_sensor_t *dev, imu_data_t *out_data) {
    if (!dev || !dev->initialized || !out_data) return BUS_ERR_INVALID_ARG;

    /* Пакетне зчитування 12 послідовних байтів: Accel (X,Y,Z = 6 байтів) + Gyro (X,Y,Z = 6 байтів) */
    uint8_t raw_buf[12];
    bus_status_t status = bus_read_reg(dev->bus, IMU_REG_ACC_X_LSB, raw_buf, sizeof(raw_buf));
    if (status != BUS_OK) {
        return status;
    }

    /* Розпакування 16-бітних знакових чисел у форматі Little-Endian (доповнення до 2) */
    int16_t raw_ax = (int16_t)((uint16_t)raw_buf[0]  | ((uint16_t)raw_buf[1]  << 8));
    int16_t raw_ay = (int16_t)((uint16_t)raw_buf[2]  | ((uint16_t)raw_buf[3]  << 8));
    int16_t raw_az = (int16_t)((uint16_t)raw_buf[4]  | ((uint16_t)raw_buf[5]  << 8));

    int16_t raw_gx = (int16_t)((uint16_t)raw_buf[6]  | ((uint16_t)raw_buf[7]  << 8));
    int16_t raw_gy = (int16_t)((uint16_t)raw_buf[8]  | ((uint16_t)raw_buf[9]  << 8));
    int16_t raw_gz = (int16_t)((uint16_t)raw_buf[10] | ((uint16_t)raw_buf[11] << 8));

    out_data->accel_mps2.x = (float)raw_ax * dev->accel_scale;
    out_data->accel_mps2.y = (float)raw_ay * dev->accel_scale;
    out_data->accel_mps2.z = (float)raw_az * dev->accel_scale;

    out_data->gyro_rads.x  = (float)raw_gx * dev->gyro_scale;
    out_data->gyro_rads.y  = (float)raw_gy * dev->gyro_scale;
    out_data->gyro_rads.z  = (float)raw_gz * dev->gyro_scale;

    /* Зчитування 2 байтів температури */
    uint8_t temp_buf[2];
    status = bus_read_reg(dev->bus, IMU_REG_TEMP_LSB, temp_buf, sizeof(temp_buf));
    if (status == BUS_OK) {
        int16_t raw_temp = (int16_t)((uint16_t)temp_buf[0] | ((uint16_t)temp_buf[1] << 8));
        out_data->temp_deg_c = 23.0f + ((float)raw_temp / 512.0f);
    } else {
        out_data->temp_deg_c = 0.0f;
    }

    return BUS_OK;
}
