#include "esp32_camera_wrapper.hpp"
#include <esp_log.h>
#include <esp_system.h>

static const char* TAG = "Esp32CameraWrapper";

camera_config_t CameraConfig::toEspCameraConfig() const {
    camera_config_t cfg;
    memset(&cfg, 0, sizeof(camera_config_t));

    cfg.pin_pwdn     = pin_pwdn;
    cfg.pin_reset    = pin_reset;
    cfg.pin_xclk     = pin_xclk;
    cfg.pin_sscb_sda = pin_siod;
    cfg.pin_sscb_scl = pin_sioc;

    cfg.pin_d7       = pin_d7;
    cfg.pin_d6       = pin_d6;
    cfg.pin_d5       = pin_d5;
    cfg.pin_d4       = pin_d4;
    cfg.pin_d3       = pin_d3;
    cfg.pin_d2       = pin_d2;
    cfg.pin_d1       = pin_d1;
    cfg.pin_d0       = pin_d0;

    cfg.pin_vsync    = pin_vsync;
    cfg.pin_href     = pin_href;
    cfg.pin_pclk     = pin_pclk;

    cfg.xclk_freq_hz = xclk_freq_hz;
    cfg.ledc_timer   = LEDC_TIMER_0;
    cfg.ledc_channel = LEDC_CHANNEL_0;

    cfg.pixel_format = pixel_format;
    cfg.frame_size   = frame_size;
    cfg.jpeg_quality = jpeg_quality;
    cfg.fb_count     = fb_count;
    cfg.grab_mode    = grab_mode;
    cfg.fb_location  = fb_location;

    return cfg;
}

// ==================== FrameBufferGuard Implementation ====================

FrameBufferGuard::FrameBufferGuard(camera_fb_t* fb) noexcept : fb_(fb) {}

FrameBufferGuard::~FrameBufferGuard() {
    reset();
}

FrameBufferGuard::FrameBufferGuard(FrameBufferGuard&& other) noexcept : fb_(other.fb_) {
    other.fb_ = nullptr;
}

FrameBufferGuard& FrameBufferGuard::operator=(FrameBufferGuard&& other) noexcept {
    if (this != &other) {
        reset();
        fb_ = other.fb_;
        other.fb_ = nullptr;
    }
    return *this;
}

void FrameBufferGuard::reset(camera_fb_t* new_fb) noexcept {
    if (fb_) {
        esp_camera_fb_return(fb_);
    }
    fb_ = new_fb;
}

camera_fb_t* FrameBufferGuard::release() noexcept {
    camera_fb_t* temp = fb_;
    fb_ = nullptr;
    return temp;
}

// ==================== Esp32CameraWrapper Implementation ====================

Esp32CameraWrapper::~Esp32CameraWrapper() {
    if (initialized_) {
        deinit();
    }
}

bool Esp32CameraWrapper::init(const CameraConfig& config) {
    if (initialized_) {
        ESP_LOGW(TAG, "Драйвер камери вже ініціалізовано.");
        return true;
    }

    config_ = config;

    // Перевірка наявності зовнішньої оперативної пам'яті PSRAM
    if (!psramFound()) {
        ESP_LOGE(TAG, "Помилка: PSRAM не виявлено! Для ESP32-S3 відеопотоку потрібна PSRAM.");
        return false;
    }

    camera_config_t esp_cfg = config_.toEspCameraConfig();

    // Ініціалізація драйвера камери
    esp_err_t err = esp_camera_init(&esp_cfg);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Помилка ініціалізації esp_camera: 0x%x (%s)", err, esp_err_to_name(err));
        return false;
    }

    sensor_t* s = esp_camera_sensor_get();
    if (!s) {
        ESP_LOGE(TAG, "Не вдалося отримати вказівник на сенсор камери.");
        esp_camera_deinit();
        return false;
    }

    // Базове калібрування сенсора OV2640/OV5640 при старті
    if (s->id.PID == OV2640_PID) {
        s->set_vflip(s, 1);       // Інверсія за вертикаллю для стандартного монтажу
        s->set_hmirror(s, 0);
    }

    initialized_ = true;
    ESP_LOGI(TAG, "Сенсор камери успішно ініціалізовано з роздільною здатністю %d", config_.frame_size);
    return true;
}

bool Esp32CameraWrapper::deinit() {
    if (!initialized_) {
        return true;
    }

    esp_err_t err = esp_camera_deinit();
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Помилка деініціалізації камери: 0x%x", err);
        return false;
    }

    initialized_ = false;
    ESP_LOGI(TAG, "Драйвер камери успішно зупинено.");
    return true;
}

FrameBufferGuard Esp32CameraWrapper::captureFrame() {
    if (!initialized_) {
        ESP_LOGE(TAG, "Спроба захоплення каду до ініціалізації камери!");
        return FrameBufferGuard(nullptr);
    }

    camera_fb_t* fb = esp_camera_fb_get();
    if (!fb) {
        ESP_LOGE(TAG, "Помилка захоплення кадру з камери (esp_camera_fb_get повернув null)");
        return FrameBufferGuard(nullptr);
    }

    return FrameBufferGuard(fb);
}

sensor_t* Esp32CameraWrapper::getSensor() const noexcept {
    if (!initialized_) return nullptr;
    return esp_camera_sensor_get();
}

bool Esp32CameraWrapper::setFrameSize(framesize_t size) {
    sensor_t* s = getSensor();
    if (!s) return false;

    if (s->set_framesize(s, size) == 0) {
        config_.frame_size = size;
        ESP_LOGI(TAG, "Роздільну здатність камери змінено на enum ID: %d", size);
        return true;
    }
    ESP_LOGE(TAG, "Не вдалося змінити роздільну здатність.");
    return false;
}

bool Esp32CameraWrapper::setJpegQuality(int quality) {
    if (quality < 1) quality = 1;
    if (quality > 63) quality = 63;

    sensor_t* s = getSensor();
    if (!s) return false;

    if (s->set_quality(s, quality) == 0) {
        config_.jpeg_quality = quality;
        ESP_LOGI(TAG, "Якість JPEG змінена на: %d", quality);
        return true;
    }
    ESP_LOGE(TAG, "Не вдалося змінити якість JPEG.");
    return false;
}

bool Esp32CameraWrapper::setBrightness(int brightness) {
    if (brightness < -2) brightness = -2;
    if (brightness > 2) brightness = 2;

    sensor_t* s = getSensor();
    if (!s) return false;

    return (s->set_brightness(s, brightness) == 0);
}

bool Esp32CameraWrapper::setContrast(int contrast) {
    if (contrast < -2) contrast = -2;
    if (contrast > 2) contrast = 2;

    sensor_t* s = getSensor();
    if (!s) return false;

    return (s->set_contrast(s, contrast) == 0);
}

bool Esp32CameraWrapper::setSaturation(int saturation) {
    if (saturation < -2) saturation = -2;
    if (saturation > 2) saturation = 2;

    sensor_t* s = getSensor();
    if (!s) return false;

    return (s->set_saturation(s, saturation) == 0);
}

bool Esp32CameraWrapper::setVFlip(bool enable) {
    sensor_t* s = getSensor();
    if (!s) return false;

    return (s->set_vflip(s, enable ? 1 : 0) == 0);
}

bool Esp32CameraWrapper::setHMirror(bool enable) {
    sensor_t* s = getSensor();
    if (!s) return false;

    return (s->set_hmirror(s, enable ? 1 : 0) == 0);
}
