/**
 * @file imu_driver.h
 * @brief Драйвер 6-осьового IMU-сенсора на C99.
 */

#ifndef IMU_DRIVER_H_
#define IMU_DRIVER_H_

#include "bus_transaction.h"

#define IMU_REG_CHIP_ID      0x00
#define IMU_REG_PWR_CTRL     0x7D
#define IMU_REG_ACC_CONF     0x40
#define IMU_REG_GYR_CONF     0x42
#define IMU_REG_ACC_X_LSB    0x12
#define IMU_REG_TEMP_LSB     0x22

#define IMU_EXPECTED_CHIP_ID 0x24

typedef struct {
    float x;
    float y;
    float z;
} imu_vec3_t;

typedef struct {
    imu_vec3_t accel_mps2; /**< Прискорення по трьох осях у м/с² */
    imu_vec3_t gyro_rads;   /**< Кутова швидкість по трьох осях у рад/с */
    float      temp_deg_c;  /**< Температура кристала в °C */
} imu_data_t;

typedef struct {
    const bus_interface_t *bus;        /**< Покажчик на уніфікований інтерфейс шини */
    float                  accel_scale;/**< Множник перетворення сирих LSB у м/с² */
    float                  gyro_scale; /**< Множник перетворення сирих LSB у рад/с */
    bool                   initialized;
} imu_sensor_t;

/**
 * @brief Ініціалізація сенсора: перевірка Chip ID та налаштування частоти опитування.
 */
bus_status_t imu_init(imu_sensor_t *dev, const bus_interface_t *bus);

/**
 * @brief Пакетне (burst) зчитування прискорень, кутових швидкостей та температури.
 */
bus_status_t imu_read_all(imu_sensor_t *dev, imu_data_t *out_data);

#endif /* IMU_DRIVER_H_ */
