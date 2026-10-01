#ifndef CAMERA_PSRAM_CONFIG_H
#define CAMERA_PSRAM_CONFIG_H

#include <stdbool.h>
#include "esp_err.h"
#include "esp_camera.h"

// Призначення виводів камери для плати Waveshare ESP32-S3R2 (роз'єм FPC)
#define CAM_PIN_PWDN     -1
#define CAM_PIN_RESET    -1
#define CAM_PIN_XCLK     10
#define CAM_PIN_SIOD     40
#define CAM_PIN_SIOC     39

#define CAM_PIN_D7       13
#define CAM_PIN_D6       11
#define CAM_PIN_D5       12
#define CAM_PIN_D4       14
#define CAM_PIN_D3       16
#define CAM_PIN_D2       18
#define CAM_PIN_D1       17
#define CAM_PIN_D0       15
#define CAM_PIN_VSYNC    38
#define CAM_PIN_HREF     47
#define CAM_PIN_PCLK     48

// Поріг для виділення подвійного кадрового буфера в Octal PSRAM (1 МБ)
#define MIN_PSRAM_FOR_DOUBLE_BUFFER (1024 * 1024)

/**
 * @brief Опитує купу на наявність та вільний обсяг псевдостатичної пам'яті (PSRAM).
 * 
 * @param[out] free_psram Доступний обсяг вільної PSRAM у байтах.
 * @param[out] min_free_psram Мінімальний зафіксований рівень вільної PSRAM.
 * @return esp_err_t ESP_OK якщо PSRAM виявлено, або ESP_ERR_NOT_FOUND якщо PSRAM відсутня.
 */
esp_err_t check_psram_availability(size_t *free_psram, size_t *min_free_psram);

/**
 * @brief Налаштовує конфігураційну структуру camera_config_t з оптимізацією під PSRAM.
 * 
 * @param[out] config Вказівник на структуру конфігурації камери ESP-IDF.
 * @param[out] uses_psram Прапор, що підтверджує розміщення кадрових буферів у PSRAM.
 * @return esp_err_t ESP_OK у разі успішного формування конфігурації.
 */
esp_err_t configure_camera_for_psram(camera_config_t *config, bool *uses_psram);

#endif // CAMERA_PSRAM_CONFIG_H
