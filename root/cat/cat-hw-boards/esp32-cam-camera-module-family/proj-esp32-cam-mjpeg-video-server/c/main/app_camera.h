#ifndef APP_CAMERA_H
#define APP_CAMERA_H

#include "esp_err.h"
#include "esp_camera.h"

// Конфігурація розпіновки шини DVP для плати ESP32-CAM (AI-Thinker)
#define CAM_PIN_PWDN    32
#define CAM_PIN_RESET   -1
#define CAM_PIN_XCLK     0
#define CAM_PIN_SIOD    26
#define CAM_PIN_SIOC    27

#define CAM_PIN_D7      35
#define CAM_PIN_D6      34
#define CAM_PIN_D5      39
#define CAM_PIN_D4      36
#define CAM_PIN_D3      21
#define CAM_PIN_D2      19
#define CAM_PIN_D1      18
#define CAM_PIN_D0       5
#define CAM_PIN_VSYNC   25
#define CAM_PIN_HREF    23
#define CAM_PIN_PCLK    22

/**
 * @brief Ініціалізація драйвера камери OV2640 з урахуванням наявності PSRAM.
 * @return ESP_OK у разі успіху або код помилки ESP-IDF.
 */
esp_err_t app_camera_init(void);

#endif // APP_CAMERA_H
