#include <cstdint>
#include "esp_camera.h"

class DvpCameraInterface {
private:
    camera_config_t config_{};

public:
    DvpCameraInterface() {
        config_.pin_pwdn     = 21;
        config_.pin_reset    = 22;
        config_.pin_xclk     = 0;
        config_.pin_sscb_sda = 26;
        config_.pin_sscb_scl = 27;

        config_.pin_d7       = 35;
        config_.pin_d6       = 34;
        config_.pin_d5       = 39;
        config_.pin_d4       = 36;
        config_.pin_d3       = 19;
        config_.pin_d2       = 18;
        config_.pin_d1       = 5;
        config_.pin_d0       = 4;

        config_.pin_vsync    = 25;
        config_.pin_href     = 23;
        config_.pin_pclk     = 22;

        config_.xclk_freq_hz = 20000000;
        config_.ledc_timer   = LEDC_TIMER_0;
        config_.ledc_channel = LEDC_CHANNEL_0;

        config_.pixel_format = PIXFORMAT_RGB565;
        config_.frame_size   = FRAMESIZE_QVGA;
        config_.jpeg_quality = 12;
        config_.fb_count     = 2;
    }

    bool initialize() {
        return (esp_camera_init(&config_) == ESP_OK);
    }
};
