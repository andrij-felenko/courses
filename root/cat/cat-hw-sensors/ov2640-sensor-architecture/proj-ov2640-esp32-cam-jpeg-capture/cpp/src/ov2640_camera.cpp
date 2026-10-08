#include "ov2640_camera.hpp"
#include <esp_log.h>
#include <driver/ledc.h>

static const char* TAG = "OV2640_CAMERA";

// Константи регістрових банків OV2640
static constexpr uint8_t BANK_SELECT_REG = 0xFF;
static constexpr uint8_t BANK_DSP        = 0x00;
static constexpr uint8_t BANK_SENSOR     = 0x01;

Ov2640Camera::~Ov2640Camera() {
    if (initialized_) {
        deinit();
    }
}

esp_err_t Ov2640Camera::init(const CameraPins& pins, framesize_t frameSize, int jpegQuality) {
    if (initialized_) {
        ESP_LOGW(TAG, "Камеру вже ініціалізовано. Повторна ініціалізація скасована.");
        return ESP_OK;
    }

    // Заповнення конфігураційної структури camera_config_t драйвера esp_camera
    config_.pin_pwdn     = pins.pin_pwdn;
    config_.pin_reset    = pins.pin_reset;
    config_.pin_xclk     = pins.pin_xclk;
    config_.pin_sscb_sda = pins.pin_sscb_sda;
    config_.pin_sscb_scl = pins.pin_sscb_scl;

    config_.pin_d7       = pins.pin_d7;
    config_.pin_d6       = pins.pin_d6;
    config_.pin_d5       = pins.pin_d5;
    config_.pin_d4       = pins.pin_d4;
    config_.pin_d3       = pins.pin_d3;
    config_.pin_d2       = pins.pin_d2;
    config_.pin_d1       = pins.pin_d1;
    config_.pin_d0       = pins.pin_d0;

    config_.pin_vsync    = pins.pin_vsync;
    config_.pin_href     = pins.pin_href;
    config_.pin_pclk     = pins.pin_pclk;

    // Генерація опорної частоти XCLK (20 МГц) через таймер LEDC
    config_.xclk_freq_hz = 20000000;
    config_.ledc_timer   = LEDC_TIMER_0;
    config_.ledc_channel = LEDC_CHANNEL_0;

    // Конфігурація формату пікселів та якості JPEG
    config_.pixel_format = PIXFORMAT_JPEG;
    config_.frame_size   = frameSize;
    config_.jpeg_quality = jpegQuality;

    // Налаштування використання зовнішьої пам'яті PSRAM для кадрових буферів
    if (psramFound()) {
        ESP_LOGI(TAG, "Зовнішню пам'ять PSRAM виявлено. Виділення буферів у PSRAM.");
        config_.fb_count = 2; // Подвійне буферизування для потокового відео без фрізів
        config_.grab_mode = CAMERA_GRAB_LATEST; // Отримання найновішого завершеного кадру
        config_.fb_location = CAMERA_FB_IN_PSRAM;
    } else {
        ESP_LOGW(TAG, "PSRAM не знайдено! Обмеження роздільної здатності та одинарний буфер у DRAM.");
        config_.fb_count = 1;
        config_.grab_mode = CAMERA_GRAB_WHEN_EMPTY;
        config_.fb_location = CAMERA_FB_IN_DRAM;
        if (config_.frame_size > FRAMESIZE_SVGA) {
            config_.frame_size = FRAMESIZE_SVGA;
        }
    }

    // Ініціалізація низькорівневого драйвера esp_camera
    esp_err_t err = esp_camera_init(&config_);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Помилка ініціалізації esp_camera: 0x%x", err);
        return err;
    }

    // Отримання покажчика на структуру керування сенсором sensor_t
    sensor_ = esp_camera_sensor_get();
    if (sensor_ == nullptr) {
        ESP_LOGE(TAG, "Не вдалося отримати покажчик на sensor_t");
        esp_camera_deinit();
        return ESP_FAIL;
    }

    // Перевірка ідентифікатора сенсора (PID OV2640 = 0x26)
    if (sensor_->id.PID == OV2640_PID) {
        ESP_LOGI(TAG, "Сенсор OV2640 успішно ідентифіковано (PID: 0x%02X)", sensor_->id.PID);
    } else {
        ESP_LOGW(TAG, "Виявлено сенсор з іншим PID: 0x%02X", sensor_->id.PID);
    }

    // Початкове вертикальне/горизонтальне дзеркалення для модуля AI-Thinker
    sensor_->set_vflip(sensor_, 1);
    sensor_->set_hmirror(sensor_, 0);

    // Оптимізація насиченості та контрасту за замовчуванням
    sensor_->set_contrast(sensor_, 0);
    sensor_->set_brightness(sensor_, 0);
    sensor_->set_saturation(sensor_, 0);

    initialized_ = true;
    ESP_LOGI(TAG, "Камеру OV2640 успішно ініціалізовано.");
    return ESP_OK;
}

esp_err_t Ov2640Camera::deinit() {
    if (!initialized_) {
        return ESP_OK;
    }

    esp_err_t err = esp_camera_deinit();
    if (err == ESP_OK) {
        initialized_ = false;
        sensor_ = nullptr;
        ESP_LOGI(TAG, "Драйвер камери деініціалізовано.");
    } else {
        ESP_LOGE(TAG, "Помилка під час деініціалізації камери: 0x%x", err);
    }
    return err;
}

FrameBufferGuard Ov2640Camera::captureFrame() {
    if (!initialized_) {
        ESP_LOGE(TAG, "Спроба захоплення каду на неініціалізованій камері!");
        return FrameBufferGuard(nullptr);
    }

    camera_fb_t* fb = esp_camera_fb_get();
    if (fb == nullptr) {
        ESP_LOGE(TAG, "Помилка захоплення кадру (esp_camera_fb_get повернув NULL)");
        return FrameBufferGuard(nullptr);
    }

    return FrameBufferGuard(fb);
}

esp_err_t Ov2640Camera::setFrameSize(framesize_t size) {
    if (!initialized_ || sensor_ == nullptr) {
        return ESP_ERR_INVALID_STATE;
    }

    esp_err_t err = sensor_->set_framesize(sensor_, size);
    if (err == ESP_OK) {
        config_.frame_size = size;
        ESP_LOGI(TAG, "Роздільну здатність змінено на enum value: %d", size);
    } else {
        ESP_LOGE(TAG, "Не вдалося змінити роздільну здатність: 0x%x", err);
    }
    return err;
}

esp_err_t Ov2640Camera::setJpegQuality(int quality) {
    if (!initialized_ || sensor_ == nullptr) {
        return ESP_ERR_INVALID_STATE;
    }

    if (quality < 0 || quality > 63) {
        return ESP_ERR_INVALID_ARG;
    }

    esp_err_t err = sensor_->set_quality(sensor_, quality);
    if (err == ESP_OK) {
        config_.jpeg_quality = quality;
        ESP_LOGI(TAG, "Якість JPEG встановлено: %d", quality);
    } else {
        ESP_LOGE(TAG, "Помилка встановлення якості JPEG: 0x%x", err);
    }
    return err;
}

esp_err_t Ov2640Camera::setBrightness(int level) {
    if (!initialized_ || sensor_ == nullptr) return ESP_ERR_INVALID_STATE;
    return sensor_->set_brightness(sensor_, level);
}

esp_err_t Ov2640Camera::setContrast(int level) {
    if (!initialized_ || sensor_ == nullptr) return ESP_ERR_INVALID_STATE;
    return sensor_->set_contrast(sensor_, level);
}

esp_err_t Ov2640Camera::setSaturation(int level) {
    if (!initialized_ || sensor_ == nullptr) return ESP_ERR_INVALID_STATE;
    return sensor_->set_saturation(sensor_, level);
}

esp_err_t Ov2640Camera::setFlip(bool hmirror, bool vflip) {
    if (!initialized_ || sensor_ == nullptr) return ESP_ERR_INVALID_STATE;
    esp_err_t err1 = sensor_->set_hmirror(sensor_, hmirror ? 1 : 0);
    esp_err_t err2 = sensor_->set_vflip(sensor_, vflip ? 1 : 0);
    return (err1 == ESP_OK && err2 == ESP_OK) ? ESP_OK : ESP_FAIL;
}

esp_err_t Ov2640Camera::writeRegister(uint8_t bank, uint8_t reg, uint8_t value) {
    if (!initialized_ || sensor_ == nullptr) {
        return ESP_ERR_INVALID_STATE;
    }

    // Для доступу до внутрішніх регістрів OV2640 спочатку перемикаємо банк (0xFF),
    // де 0x00 відповідає DSP Bank, а 0x01 — Sensor Bank.
    esp_err_t err = sensor_->set_reg(sensor_, BANK_SELECT_REG, 0xFF, bank);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Помилка перемикання регістрового банку на 0x%02X", bank);
        return err;
    }

    // Запис значення у вибраний регістр через шину SCCB
    err = sensor_->set_reg(sensor_, reg, 0xFF, value);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Помилка запису значення 0x%02X в регістр 0x%02X (Банк 0x%02X)", value, reg, bank);
    } else {
        ESP_LOGD(TAG, "Регістр 0x%02X у банку 0x%02X успішно оновлено на 0x%02X", reg, bank, value);
    }

    return err;
}
