#ifndef APP_CAMERA_H
#define APP_CAMERA_H

#include <stdbool.h>
#include <stdint.h>
#include "esp_err.h"
#include "esp_camera.h"

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @file app_camera.h
 * @brief Оголошення C-інтерфейсу конфігурації та ініціалізації сенсора OV2640.
 *
 * Модуль забезпечує призначення GPIO-виводів паралельного інтерфейсу DVP,
 * шини SCCB, тактування XCLK, перевірку наявності зовнішньої пам'яті PSRAM
 * та керування основними параметрами зображення OV2640.
 */

/* Призначення GPIO-виводів для плат модулів AI-Thinker ESP32-CAM */
#define CAM_PIN_PWDN      32
#define CAM_PIN_RESET     -1
#define CAM_PIN_XCLK      0
#define CAM_PIN_SIOD      26
#define CAM_PIN_SIOC      27

#define CAM_PIN_D7        35
#define CAM_PIN_D6        34
#define CAM_PIN_D5        39
#define CAM_PIN_D4        36
#define CAM_PIN_D3        21
#define CAM_PIN_D2        19
#define CAM_PIN_D1        18
#define CAM_PIN_D0        5
#define CAM_PIN_VSYNC     25
#define CAM_PIN_HREF      23
#define CAM_PIN_PCLK      22

/**
 * @brief Ініціалізація підсистеми камери OV2640 з урахуванням конфігурації PSRAM.
 *
 * @param frame_size Роздільна здатність кадру (наприклад, FRAMESIZE_VGA).
 * @param pixel_format Піксельний формат (наприклад, PIXFORMAT_JPEG).
 * @return esp_err_t ESP_OK при успіху, або відповідний код помилки ESP-IDF.
 */
esp_err_t app_camera_init(framesize_t frame_size, pixformat_t pixel_format);

/**
 * @brief Деініціалізація драйвера камери та вивільнення ресурсів.
 *
 * @return esp_err_t ESP_OK при успіху.
 */
esp_err_t app_camera_deinit(void);

/**
 * @brief Налаштування якості стиснення JPEG (10 - висока якість, 63 - низька якість).
 *
 * @param quality Рівень якості (10-63).
 * @return esp_err_t ESP_OK або ESP_ERR_INVALID_STATE, якщо сенсор не ініціалізовано.
 */
esp_err_t app_camera_set_quality(int quality);

/**
 * @brief Зміна роздільної здатності кадру в режимі реального часу.
 *
 * @param frame_size Нова роздільна здатність.
 * @return esp_err_t ESP_OK або код помилки.
 */
esp_err_t app_camera_set_framesize(framesize_t frame_size);

/**
 * @brief Керування вертикальним віддзеркаленням кадру (VFLIP).
 *
 * @param enable 1 - увімкнути віддзеркалення, 0 - вимкнути.
 * @return esp_err_t ESP_OK або код помилки.
 */
esp_err_t app_camera_set_vflip(int enable);

/**
 * @brief Керування горизонтальним віддзеркаленням кадру (HMIRROR).
 *
 * @param enable 1 - увімкнути віддзеркалення, 0 - вимкнути.
 * @return esp_err_t ESP_OK або код помилки.
 */
esp_err_t app_camera_set_hmirror(int enable);

/**
 * @brief Перевірка доступності зовнішньої оперативної пам'яті PSRAM.
 *
 * @return true Якщо PSRAM ініціалізовано і доступно для кадрових буферів.
 */
bool app_camera_is_psram_available(void);

#ifdef __cplusplus
}
#endif

#endif /* APP_CAMERA_H */
