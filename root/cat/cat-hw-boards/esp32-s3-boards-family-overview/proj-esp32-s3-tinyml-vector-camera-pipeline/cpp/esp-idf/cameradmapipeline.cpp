#include "esp_camera.h"
#include "esp_log.h"

class CameraDmaPipeline {
private:
    camera_config_t config_;
    static constexpr const char* TAG = "CameraDmaPipeline";

public:
    CameraDmaPipeline() {
        config_ = {};
        config_.pin_pwdn     = -1;
        config_.pin_reset    = -1;
        config_.pin_xclk     = 10;
        config_.pin_sccb_sda = 40;
        config_.pin_sccb_scl = 39;
        config_.pin_d7       = 35;
        config_.pin_d6       = 36;
        config_.pin_d5       = 37;
        config_.pin_d4       = 38;
        config_.pin_d3       = 4;
        config_.pin_d2       = 5;
        config_.pin_d1       = 6;
        config_.pin_d0       = 7;
        config_.pin_vsync    = 8;
        config_.pin_href     = 9;
        config_.pin_pclk     = 11;
        config_.xclk_freq_hz = 20000000;
        config_.pixel_format = PIXFORMAT_RGB565;
        config_.frame_size   = FRAMESIZE_QVGA;
        config_.fb_count     = 2;
        config_.grab_mode    = CAMERA_GRAB_LATEST;
        config_.fb_location  = CAMERA_FB_IN_PSRAM;
    }

    esp_err_t initialize() {
        esp_err_t err = esp_camera_init(&config_);
        if (err != ESP_OK) {
            ESP_LOGE(TAG, "Збій налаштування периферії LCD_CAM: 0x%x", err);
            return err;
        }
        return ESP_OK;
    }

    camera_fb_t* get_frame() {
        return esp_camera_fb_get();
    }

    void return_frame(camera_fb_t* fb) {
        esp_camera_fb_return(fb);
    }
};
