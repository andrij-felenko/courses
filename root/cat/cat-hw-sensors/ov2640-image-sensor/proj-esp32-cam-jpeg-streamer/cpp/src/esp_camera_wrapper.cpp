#include "esp_camera_wrapper.hpp"
#include <esp_system.h>

#if __has_include(<esp_psram.h>)
#include <esp_psram.h>
#endif

EspCamera::EspCamera(const CameraPinConfig& pin_config)
    : pin_config_(pin_config), initialized_(false), psram_available_(false) {
}

EspCamera::~EspCamera() {
    deinit();
}

bool EspCamera::init(framesize_t frame_size, pixformat_t pixel_format) {
    if (initialized_) {
        Serial.println(F("[EspCamera] Камеру вже ініціалізовано!"));
        return true;
    }

    // Перевірка наявності та доступності PSRAM
    psram_available_ = psramFound();
    if (psram_available_) {
        Serial.println(F("[EspCamera] Виявлено PSRAM. Активація режиму високої роздільності та подвійної буферизації."));
        mode_config_.frame_size   = frame_size;
        mode_config_.pixel_format = pixel_format;
        mode_config_.jpeg_quality = 10;
        mode_config_.fb_count     = 2;
        mode_config_.grab_mode    = CAMERA_GRAB_LATEST;
    } else {
        Serial.println(F("[EspCamera] УВАГА: PSRAM не знайдено! Використовується обмежувальний режим для SRAM."));
        mode_config_.frame_size   = (frame_size > FRAMESIZE_SVGA) ? FRAMESIZE_SVGA : frame_size;
        mode_config_.pixel_format = pixel_format;
        mode_config_.jpeg_quality = 15;
        mode_config_.fb_count     = 1;
        mode_config_.grab_mode    = CAMERA_GRAB_WHEN_EMPTY;
    }

    // Налаштування структури драйвера esp32-camera
    camera_config_t config;
    config.pin_pwdn     = pin_config_.pin_pwdn;
    config.pin_reset    = pin_config_.pin_reset;
    config.pin_xclk     = pin_config_.pin_xclk;
    config.pin_sccb_sda = pin_config_.pin_siod;
    config.pin_sccb_scl = pin_config_.pin_sioc;

    config.pin_d7       = pin_config_.pin_d7;
    config.pin_d6       = pin_config_.pin_d6;
    config.pin_d5       = pin_config_.pin_d5;
    config.pin_d4       = pin_config_.pin_d4;
    config.pin_d3       = pin_config_.pin_d3;
    config.pin_d2       = pin_config_.pin_d2;
    config.pin_d1       = pin_config_.pin_d1;
    config.pin_d0       = pin_config_.pin_d0;

    config.pin_vsync    = pin_config_.pin_vsync;
    config.pin_href     = pin_config_.pin_href;
    config.pin_pclk     = pin_config_.pin_pclk;

    config.xclk_freq_hz = mode_config_.xclk_freq_hz;
    config.ledc_timer   = LEDC_TIMER_0;
    config.ledc_channel = LEDC_CHANNEL_0;

    config.pixel_format = mode_config_.pixel_format;
    config.frame_size   = mode_config_.frame_size;
    config.jpeg_quality = mode_config_.jpeg_quality;
    config.fb_count     = mode_config_.fb_count;
    config.grab_mode    = mode_config_.grab_mode;
    config.fb_location  = psram_available_ ? CAMERA_FB_IN_PSRAM : CAMERA_FB_IN_DRAM;

    // Скидання камери через PWDN (якщо вивід доступний)
    if (pin_config_.pin_pwdn != -1) {
        pinMode(pin_config_.pin_pwdn, OUTPUT);
        digitalWrite(pin_config_.pin_pwdn, HIGH);
        delay(10);
        digitalWrite(pin_config_.pin_pwdn, LOW);
        delay(10);
    }

    // Ініціалізація низькорівневого драйвера
    esp_err_t err = esp_camera_init(&config);
    if (err != ESP_OK) {
        Serial.printf("[EspCamera] Помилка ініціалізації драйвера камери: 0x%x\n", err);
        return false;
    }

    // Розпізнавання сенсора та встановлення дефолтних налаштувань через SCCB
    sensor_t* s = getSensor();
    if (s != nullptr) {
        if (s->id.PID == OV2640_PID) {
            Serial.println(F("[EspCamera] Сенсор OV2640 успішно ідентифіковано."));
            s->set_vflip(s, 1);       // Вертикальний розворот кадру
            s->set_hmirror(s, 0);     // Без горизонтального дзеркалювання
            s->set_brightness(s, 0);  // Початкова яскравість (0)
            s->set_contrast(s, 0);    // Початковий контраст (0)
        } else {
            Serial.printf("[EspCamera] Виявлено сенсор з PID=0x%x (очікувався OV2640)\n", s->id.PID);
        }
    } else {
        Serial.println(F("[EspCamera] Не вдалося отримати дескриптор sensor_t!"));
        esp_camera_deinit();
        return false;
    }

    initialized_ = true;
    Serial.println(F("[EspCamera] Успішна ініціалізація системи зображення!"));
    return true;
}

void EspCamera::deinit() {
    if (initialized_) {
        esp_camera_deinit();
        initialized_ = false;
        Serial.println(F("[EspCamera] Драйвер камери деініціалізовано."));
    }
}

FrameBufferGuard EspCamera::captureFrame() {
    if (!initialized_) {
        Serial.println(F("[EspCamera] Спроба захоплення каду на неініціалізованій камері!"));
        return FrameBufferGuard(nullptr);
    }
    camera_fb_t* fb = esp_camera_fb_get();
    if (!fb) {
        Serial.println(F("[EspCamera] Помилка отримати кадр з модуля OV2640!"));
    }
    return FrameBufferGuard(fb);
}

sensor_t* EspCamera::getSensor() const {
    if (!initialized_ && esp_camera_sensor_get() == nullptr) {
        return esp_camera_sensor_get();
    }
    return esp_camera_sensor_get();
}

bool EspCamera::setBrightness(int level) {
    sensor_t* s = getSensor();
    return (s && s->set_brightness) ? (s->set_brightness(s, level) == 0) : false;
}

bool EspCamera::setContrast(int level) {
    sensor_t* s = getSensor();
    return (s && s->set_contrast) ? (s->set_contrast(s, level) == 0) : false;
}

bool EspCamera::setSaturation(int level) {
    sensor_t* s = getSensor();
    return (s && s->set_saturation) ? (s->set_saturation(s, level) == 0) : false;
}

bool EspCamera::setQuality(int quality) {
    sensor_t* s = getSensor();
    return (s && s->set_quality) ? (s->set_quality(s, quality) == 0) : false;
}

bool EspCamera::setFrameSize(framesize_t size) {
    sensor_t* s = getSensor();
    return (s && s->set_framesize) ? (s->set_framesize(s, size) == 0) : false;
}

bool EspCamera::setVFlip(bool enable) {
    sensor_t* s = getSensor();
    return (s && s->set_vflip) ? (s->set_vflip(s, enable ? 1 : 0) == 0) : false;
}

bool EspCamera::setHMirror(bool enable) {
    sensor_t* s = getSensor();
    return (s && s->set_hmirror) ? (s->set_hmirror(s, enable ? 1 : 0) == 0) : false;
}

bool EspCamera::setSpecialEffect(int effect) {
    sensor_t* s = getSensor();
    return (s && s->set_special_effect) ? (s->set_special_effect(s, effect) == 0) : false;
}
