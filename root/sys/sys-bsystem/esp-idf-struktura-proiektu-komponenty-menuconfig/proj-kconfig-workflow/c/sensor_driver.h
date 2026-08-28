/* include/sensor_driver.h (C) */
#pragma once

#include <stdint.h>
#include <stdbool.h>
#include "esp_err.h"
#include "sdkconfig.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    float temperature_celsius;
    float humidity_percent;
    uint32_t timestamp_ms;
} sensor_reading_t;

/**
 * @brief Ініціалізація шини I2C, створення м'ютекса та калібрування сенсора.
 * @return ESP_OK у разі успіху або відповідний код помилки esp_err_t.
 */
esp_err_t sensor_driver_init(void);

/**
 * @brief Потокобезпечне зчитування фізичних параметрів із сенсора.
 * @param[out] out_reading Вказівник на структуру для збереження результату.
 */
esp_err_t sensor_driver_read(sensor_reading_t *out_reading);

/**
 * @brief Зупинка роботи, видалення драйвера I2C та вивільнення пам'яті.
 */
esp_err_t sensor_driver_deinit(void);

#ifdef __cplusplus
}
#endif
