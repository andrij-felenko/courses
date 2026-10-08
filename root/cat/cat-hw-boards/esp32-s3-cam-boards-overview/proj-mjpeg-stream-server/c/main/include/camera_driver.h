#ifndef CAMERA_DRIVER_H
#define CAMERA_DRIVER_H

#include <stdint.h>
#include <stdbool.h>
#include "esp_err.h"
#include "esp_camera.h"

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Прив'язка контактів DVP-інтерфейсу камери для плати ESP32-S3-CAM
 */
#define CAM_PIN_PWDN      -1
#define CAM_PIN_RESET     -1
#define CAM_PIN_XCLK      15
#define CAM_PIN_SIOD      4   /* I2C SCCB SDA */
#define CAM_PIN_SIOC      5   /* I2C SCCB SCL */

#define CAM_PIN_D7        16
#define CAM_PIN_D6        17
#define CAM_PIN_D5        18
#define CAM_PIN_D4        12
#define CAM_PIN_D3        10
#define CAM_PIN_D2        8
#define CAM_PIN_D1        9
#define CAM_PIN_D0        11
#define CAM_PIN_VSYNC     6
#define CAM_PIN_HREF      7
#define CAM_PIN_PCLK      13

#define CAM_XCLK_FREQ_HZ  20000000

/**
 * @brief Ініціалізація DVP-камери на базі сенсора OV2640/OV5640.
 *
 * Виконує налаштування GPIO, генерацію тактового сигналу XCLK, ініціалізацію SCCB
 * та виділення подвійного кадрового буфера в зовнішній пам'яті PSRAM через шину Octal SPI.
 *
 * @return esp_err_t ESP_OK у разі успішної ініціалізації
 */
esp_err_t camera_driver_init(void);

/**
 * @brief Захоплення поточного кадру з DVP-камери.
 *
 * @return esp_camera_fb_t* Указник на структуру буфера кадру або NULL у разі помилки
 */
esp_camera_fb_t* camera_driver_capture_frame(void);

/**
 * @brief Повернення кадрового буфера назад у драйвер після обробки/відправки.
 *
 * @param fb Указник на буфер кадру, отриманий від camera_driver_capture_frame
 */
void camera_driver_return_frame(esp_camera_fb_t *fb);

/**
 * @brief Деініціалізація драйвера камери та звільнення ресурсів.
 *
 * @return esp_err_t ESP_OK у разі успіху
 */
esp_err_t camera_driver_deinit(void);

#ifdef __cplusplus
}
#endif

#endif /* CAMERA_DRIVER_H */
