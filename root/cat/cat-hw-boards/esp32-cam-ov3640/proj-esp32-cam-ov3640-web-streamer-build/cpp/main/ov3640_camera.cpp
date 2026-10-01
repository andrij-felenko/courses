#include "ov3640_camera.hpp"
#include "esp_log.h"
#include "esp_psram.h"

static const char* TAG = "Ov3640Camera";

Ov3640Camera::~Ov3640Camera() {
    if (initialized_) {
        esp_camera_deinit();
        ESP_LOGI(TAG, "Драйвер камери деініціалізовано.");
    }
}

void Ov3640Camera::setupPinConfig() {
    config_.ledc_channel = LEDC_CHANNEL_0;
    config_.ledc_timer = LEDC_TIMER_0;
    config_.pin_d0 = 5;
    config_.pin_d1 = 18;
    config_.pin_d2 = 19;
    config_.pin_d3 = 21;
    config_.pin_d4 = 36;
    config_.pin_d5 = 39;
    config_.pin_d6 = 34;
    config_.pin_d7 = 35;
    config_.pin_xclk = 0;
    config_.pin_pclk = 22;
    config_.pin_vsync = 25;
    config_.pin_href = 23;
    config_.pin_sccb_sda = 26;
    config_.pin_sccb_scl = 27;
    config_.pin_pwdn = 32;
    config_.pin_reset = -1;
    config_.xclk_freq_hz = 20000000;
    config_.pixel_format = PIXFORMAT_JPEG;
}

esp_err_t Ov3640Camera::init() {
    setupPinConfig();

    if (esp_psram_is_initialized()) {
        config_.frame_size = FRAMESIZE_QXGA; // 2048x1536 (3 МП)
        config_.jpeg_quality = 12;
        config_.fb_count = 2;
        config_.grab_mode = CAMERA_GRAB_LATEST;
        ESP_LOGI(TAG, "PSRAM активна: налаштовано роздільність QXGA та подвійну буферизацію.");
    } else {
        config_.frame_size = FRAMESIZE_SVGA;
        config_.jpeg_quality = 15;
        config_.fb_count = 1;
        config_.grab_mode = CAMERA_GRAB_WHEN_EMPTY;
        ESP_LOGW(TAG, "PSRAM відсутня: обмежено до SVGA, один кадровий буфер.");
    }

    esp_err_t err = esp_camera_init(&config_);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Помилка ініціалізації esp_camera: 0x%x", err);
        return err;
    }

    initialized_ = true;
    ESP_LOGI(TAG, "Сенсор OV3640 успішно ініціалізовано.");
    return ESP_OK;
}

FrameBufferGuard Ov3640Camera::captureFrame() {
    if (!initialized_) {
        ESP_LOGE(TAG, "Камеру не ініціалізовано перед захопленням кадру!");
        return FrameBufferGuard(nullptr);
    }
    camera_fb_t* fb = esp_camera_fb_get();
    if (!fb) {
        ESP_LOGE(TAG, "Збій захоплення фрейму з матриці!");
    }
    return FrameBufferGuard(fb);
}

esp_err_t Ov3640Camera::setFramesize(framesize_t size) {
    sensor_t* s = esp_camera_sensor_get();
    if (!s) return ESP_FAIL;
    return s->set_framesize(s, size);
}

esp_err_t Ov3640Camera::setBrightness(int level) {
    sensor_t* s = esp_camera_sensor_get();
    if (!s) return ESP_FAIL;
    return s->set_brightness(s, level);
}
