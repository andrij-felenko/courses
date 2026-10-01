#ifndef APP_CAMERA_H
#define APP_CAMERA_H

#include "esp_camera.h"
#include "esp_err.h"

// Розпіновка DVP-шини камери OV3640 на модулі ESP32-CAM (AI-Thinker)
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

// Функції ініціалізації та захоплення кадрів
esp_err_t app_camera_init(void);
camera_fb_t* app_camera_take_picture(void);
void app_camera_release_picture(camera_fb_t *fb);

#endif // APP_CAMERA_H
