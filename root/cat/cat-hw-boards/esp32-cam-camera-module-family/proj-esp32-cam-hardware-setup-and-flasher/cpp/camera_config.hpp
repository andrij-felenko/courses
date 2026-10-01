#ifndef CAMERA_CONFIG_HPP
#define CAMERA_CONFIG_HPP

#include "esp_camera.h"
#include <esp_system.h>

// Модель плати: AI-THINKER ESP32-CAM
namespace CameraPins {
    constexpr int PWDN     = 32;
    constexpr int RESET    = -1;
    constexpr int XCLK     = 0;
    constexpr int SIOD     = 26;
    constexpr int SIOC     = 27;

    constexpr int Y9       = 35;
    constexpr int Y8       = 34;
    constexpr int Y7       = 39;
    constexpr int Y6       = 36;
    constexpr int Y5       = 21;
    constexpr int Y4       = 19;
    constexpr int Y3       = 18;
    constexpr int Y2       = 5;
    constexpr int VSYNC    = 25;
    constexpr int HREF     = 23;
    constexpr int PCLK     = 22;
}

// Клас-обгортка для керування ініціалізацією камери OV2640
class CameraManager {
public:
    CameraManager() = default;
    ~CameraManager() = default;

    // Конфігурація та ініціалізація драйвера esp_camera
    bool init() {
        camera_config_t config;
        config.ledc_channel = LEDC_CHANNEL_0;
        config.ledc_timer   = LEDC_TIMER_0;
        config.pin_d0       = CameraPins::Y2;
        config.pin_d1       = CameraPins::Y3;
        config.pin_d2       = CameraPins::Y4;
        config.pin_d3       = CameraPins::Y5;
        config.pin_d4       = CameraPins::Y6;
        config.pin_d5       = CameraPins::Y7;
        config.pin_d6       = CameraPins::Y8;
        config.pin_d7       = CameraPins::Y9;
        config.pin_xclk     = CameraPins::XCLK;
        config.pin_pclk     = CameraPins::PCLK;
        config.pin_vsync    = CameraPins::VSYNC;
        config.pin_href     = CameraPins::HREF;
        config.pin_sccb_sda = CameraPins::SIOD;
        config.pin_sccb_scl = CameraPins::SIOC;
        config.pin_pwdn     = CameraPins::PWDN;
        config.pin_reset    = CameraPins::RESET;
        config.xclk_freq_hz = 20000000;
        config.pixel_format = PIXFORMAT_JPEG;

        // Вибір розміру кадру залежно від наявності PSRAM
        if (psramFound()) {
            config.frame_size = FRAMESIZE_UXGA; // 1600x1200
            config.jpeg_quality = 10;
            config.fb_count = 2; // Подвійна буферизація
        } else {
            config.frame_size = FRAMESIZE_SVGA; // 800x600
            config.jpeg_quality = 12;
            config.fb_count = 1;
        }

        // Ініціалізація драйвера
        esp_err_t err = esp_camera_init(&config);
        return (err == ESP_OK);
    }
};

#endif // CAMERA_CONFIG_HPP
