#include "camera_manager.hpp"
#include "camera_pins.hpp"
#include "esp_log.h"
#include "esp_system.h"
#include <utility>

namespace esp32_cam {

static const char* TAG = "CameraManager";

// --- Реалізація RAII-класу FrameBuffer ---

FrameBuffer::FrameBuffer(camera_fb_t* fb) noexcept : fb_(fb) {}

FrameBuffer::~FrameBuffer() {
    release();
}

FrameBuffer::FrameBuffer(FrameBuffer&& other) noexcept : fb_(other.fb_) {
    other.fb_ = nullptr;
}

FrameBuffer& FrameBuffer::operator=(FrameBuffer&& other) noexcept {
    if (this != &other) {
        release();
        fb_ = other.fb_;
        other.fb_ = nullptr;
    }
    return *this;
}

void FrameBuffer::release() noexcept {
    if (fb_) {
        esp_camera_fb_return(fb_);
        fb_ = nullptr;
    }
}

// --- Реалізація класу CameraManager ---

CameraManager::~CameraManager() {
    if (initialized_) {
        esp_camera_deinit();
        initialized_ = false;
        ESP_LOGI(TAG, "Драйвер камери деініціалізовано");
    }
}

camera_config_t CameraManager::make_default_config() const noexcept {
    camera_config_t config{};
    config.ledc_channel = LEDC_CHANNEL_0;
    config.ledc_timer   = LEDC_TIMER_0;

    config.pin_d0       = CameraPins::d0;
    config.pin_d1       = CameraPins::d1;
    config.pin_d2       = CameraPins::d2;
    config.pin_d3       = CameraPins::d3;
    config.pin_d4       = CameraPins::d4;
    config.pin_d5       = CameraPins::d5;
    config.pin_d6       = CameraPins::d6;
    config.pin_d7       = CameraPins::d7;

    config.pin_xclk     = CameraPins::xclk;
    config.pin_pclk     = CameraPins::pclk;
    config.pin_vsync    = CameraPins::vsync;
    config.pin_href     = CameraPins::href;
    config.pin_sscb_sda = CameraPins::siod;
    config.pin_sscb_scl = CameraPins::sioc;
    config.pin_pwdn     = CameraPins::pwdn;
    config.pin_reset    = CameraPins::reset;

    config.xclk_freq_hz = 20000000;
    config.pixel_format = PIXFORMAT_JPEG;

    if (psramFound()) {
        config.frame_size   = FRAMESIZE_UXGA;
        config.jpeg_quality = 10;
        config.fb_count     = 2;
        config.grab_mode    = CAMERA_GRAB_LATEST;
        ESP_LOGI(TAG, "Виявлено PSRAM: режим UXGA з подвійною буферизацією");
    } else {
        config.frame_size   = FRAMESIZE_SVGA;
        config.jpeg_quality = 12;
        config.fb_count     = 1;
        config.grab_mode    = CAMERA_GRAB_WHEN_EMPTY;
        ESP_LOGW(TAG, "PSRAM відсутня: обмеження роздільної здатності SVGA");
    }

    return config;
}

esp_err_t CameraManager::init() noexcept {
    if (initialized_) {
        ESP_LOGW(TAG, "Камера вже ініціалізована");
        return ESP_OK;
    }

    const camera_config_t config = make_default_config();
    const esp_err_t err = esp_camera_init(&config);

    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Помилка низькорівневої ініціалізації камери: 0x%x (%s)", err, esp_err_to_name(err));
        return err;
    }

    initialized_ = true;
    ESP_LOGI(TAG, "Успішна ініціалізація C++ модуля CameraManager");
    return ESP_OK;
}

FrameBuffer CameraManager::capture_frame() noexcept {
    if (!initialized_) {
        ESP_LOGE(TAG, "Спроба захоплення каду без попередньої ініціалізації");
        return FrameBuffer{nullptr};
    }

    camera_fb_t* fb = esp_camera_fb_get();
    if (!fb) {
        ESP_LOGE(TAG, "Не вдалося одержати camera_fb_t від сенсора");
        return FrameBuffer{nullptr};
    }

    return FrameBuffer{fb};
}

} // namespace esp32_cam
