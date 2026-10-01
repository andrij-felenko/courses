#ifndef CAMERA_PINS_OV3640_HPP
#define CAMERA_PINS_OV3640_HPP

#include "esp_camera.h"

// Конфігурація розпіновки DVP-шини камери OV3640 для модуля AI-Thinker ESP32-CAM.
namespace CameraPins {
    constexpr int PWDN_GPIO_NUM  = 32;
    constexpr int RESET_GPIO_NUM = -1;
    constexpr int XCLK_GPIO_NUM  = 0;
    constexpr int SIOD_GPIO_NUM  = 26;
    constexpr int SIOC_GPIO_NUM  = 27;

    constexpr int Y9_GPIO_NUM    = 35;
    constexpr int Y8_GPIO_NUM    = 34;
    constexpr int Y7_GPIO_NUM    = 39;
    constexpr int Y6_GPIO_NUM    = 36;
    constexpr int Y5_GPIO_NUM    = 21;
    constexpr int Y4_GPIO_NUM    = 19;
    constexpr int Y3_GPIO_NUM    = 18;
    constexpr int Y2_GPIO_NUM    = 5;

    constexpr int VSYNC_GPIO_NUM = 25;
    constexpr int HREF_GPIO_NUM  = 23;
    constexpr int PCLK_GPIO_NUM  = 22;
}

// Формує конфігураційну структуру для ініціалізації драйвера камери.
inline camera_config_t createOV3640Config() {
    camera_config_t config;
    config.ledc_channel = LEDC_CHANNEL_0;
    config.ledc_timer   = LEDC_TIMER_0;
    config.pin_d0       = CameraPins::Y2_GPIO_NUM;
    config.pin_d1       = CameraPins::Y3_GPIO_NUM;
    config.pin_d2       = CameraPins::Y4_GPIO_NUM;
    config.pin_d3       = CameraPins::Y5_GPIO_NUM;
    config.pin_d4       = CameraPins::Y6_GPIO_NUM;
    config.pin_d5       = CameraPins::Y7_GPIO_NUM;
    config.pin_d6       = CameraPins::Y8_GPIO_NUM;
    config.pin_d7       = CameraPins::Y9_GPIO_NUM;
    config.pin_xclk     = CameraPins::XCLK_GPIO_NUM;
    config.pin_pclk     = CameraPins::PCLK_GPIO_NUM;
    config.pin_vsync    = CameraPins::VSYNC_GPIO_NUM;
    config.pin_href     = CameraPins::HREF_GPIO_NUM;
    config.pin_sscb_sda = CameraPins::SIOD_GPIO_NUM;
    config.pin_sscb_scl = CameraPins::SIOC_GPIO_NUM;
    config.pin_pwdn     = CameraPins::PWDN_GPIO_NUM;
    config.pin_reset    = CameraPins::RESET_GPIO_NUM;
    config.xclk_freq_hz = 20000000;
    config.pixel_format = PIXFORMAT_JPEG;

    // Перевірка наявності PSRAM для вибору роздільності та кількості буферів.
    if (psramFound()) {
        config.frame_size   = FRAMESIZE_UXGA; // 1600x1200 для 2-МП сенсора OV3640
        config.jpeg_quality = 12;
        config.fb_count     = 2;
        config.grab_mode    = CAMERA_GRAB_LATEST;
    } else {
        config.frame_size   = FRAMESIZE_SVGA;
        config.jpeg_quality = 15;
        config.fb_count     = 1;
        config.grab_mode    = CAMERA_GRAB_WHEN_EMPTY;
    }

    return config;
}

#endif // CAMERA_PINS_OV3640_HPP
