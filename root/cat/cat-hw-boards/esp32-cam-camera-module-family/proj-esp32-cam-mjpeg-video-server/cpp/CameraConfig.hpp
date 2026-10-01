#ifndef CAMERA_CONFIG_HPP
#define CAMERA_CONFIG_HPP

#include "esp_camera.h"

// Прив'язка виводів DVP-шини камери OV2640 для модуля AI-Thinker ESP32-CAM
namespace Esp32CamPinout {
    constexpr int PWDN  = 32;
    constexpr int RESET = -1;
    constexpr int XCLK  = 0;
    constexpr int SIOD  = 26;
    constexpr int SIOC  = 27;

    constexpr int Y9    = 35;
    constexpr int Y8    = 34;
    constexpr int Y7    = 39;
    constexpr int Y6    = 36;
    constexpr int Y5    = 21;
    constexpr int Y4    = 19;
    constexpr int Y3    = 18;
    constexpr int Y2    = 5;
    constexpr int VSYNC = 25;
    constexpr int HREF  = 23;
    constexpr int PCLK  = 22;
}

// Формування структури конфігурації камери для модуля AI-Thinker
inline camera_config_t get_ai_thinker_camera_config() {
    camera_config_t config{};
    config.ledc_channel = LEDC_CHANNEL_0;
    config.ledc_timer   = LEDC_TIMER_0;
    config.pin_d0       = Esp32CamPinout::Y2;
    config.pin_d1       = Esp32CamPinout::Y3;
    config.pin_d2       = Esp32CamPinout::Y4;
    config.pin_d3       = Esp32CamPinout::Y5;
    config.pin_d4       = Esp32CamPinout::Y6;
    config.pin_d5       = Esp32CamPinout::Y7;
    config.pin_d6       = Esp32CamPinout::Y8;
    config.pin_d7       = Esp32CamPinout::Y9;
    config.pin_xclk     = Esp32CamPinout::XCLK;
    config.pin_pclk     = Esp32CamPinout::PCLK;
    config.pin_vsync    = Esp32CamPinout::VSYNC;
    config.pin_href     = Esp32CamPinout::HREF;
    config.pin_siod     = Esp32CamPinout::SIOD;
    config.pin_sioc     = Esp32CamPinout::SIOC;
    config.pin_pwdn     = Esp32CamPinout::PWDN;
    config.pin_reset    = Esp32CamPinout::RESET;
    config.xclk_freq_hz = 20000000;
    config.pixel_format = PIXFORMAT_JPEG;

    // Перевірка наявності зовнішньої пам'яті PSRAM
    if (psramFound()) {
        config.frame_size = FRAMESIZE_VGA;
        config.jpeg_quality = 10;
        config.fb_count = 2;
        config.grab_mode = CAMERA_GRAB_LATEST;
    } else {
        config.frame_size = FRAMESIZE_SVGA;
        config.jpeg_quality = 12;
        config.fb_count = 1;
        config.grab_mode = CAMERA_GRAB_WHEN_EMPTY;
    }

    return config;
}

#endif // CAMERA_CONFIG_HPP
