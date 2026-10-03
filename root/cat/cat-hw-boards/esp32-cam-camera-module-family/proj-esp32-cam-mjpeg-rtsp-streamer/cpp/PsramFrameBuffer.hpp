#ifndef PSRAM_FRAME_BUFFER_HPP
#define PSRAM_FRAME_BUFFER_HPP

#include <esp_camera.h>
#include <esp_system.h>
#include <esp_log.h>
#include <Arduino.h>
#include <cstdint>
#include <utility>

/**
 * @brief Клас для безпечного RAII-управління захопленим кадром камери.
 * 
 * Гарантує повернення кадрового буфера драйверу esp_camera після завершення
 * області видимості об'єкта Frame, запобігаючи витокам пам'яті PSRAM.
 */
class Frame {
public:
    explicit Frame(camera_fb_t* fb = nullptr) noexcept : fb_(fb) {}

    ~Frame() {
        release();
    }

    // Забороняємо копіювання (власність на кадр унікальна)
    Frame(const Frame&) = delete;
    Frame& operator=(const Frame&) = delete;

    // Семантика переміщення
    Frame(Frame&& other) noexcept : fb_(other.fb_) {
        other.fb_ = nullptr;
    }

    Frame& operator=(Frame&& other) noexcept {
        if (this != &other) {
            release();
            fb_ = other.fb_;
            other.fb_ = nullptr;
        }
        return *this;
    }

    /**
     * @brief Перевіряє валідність буфера кадра.
     */
    bool isValid() const {
        return fb_ != nullptr && fb_->buf != nullptr && fb_->len > 0;
    }

    /**
     * @brief Отримує вказівник на дані кадра (байти JPEG).
     */
    const uint8_t* data() const {
        return fb_ ? fb_->buf : nullptr;
    }

    /**
     * @brief Отримує розмір даних кадра в байтах.
     */
    size_t size() const {
        return fb_ ? fb_->len : 0;
    }

    /**
     * @brief Отримує формат пікселів зображення.
     */
    pixformat_t format() const {
        return fb_ ? fb_->format : PIXFORMAT_JPEG;
    }

    /**
     * @brief Явне вивільнення буфера кадра назад у драйвер камери.
     */
    void release() {
        if (fb_) {
            esp_camera_fb_return(fb_);
            fb_ = nullptr;
        }
    }

private:
    camera_fb_t* fb_{nullptr};
};

/**
 * @brief Обгортка драйвера камери ESP32-CAM із підтримкою виділення пам'яті в PSRAM.
 * 
 * Конфігурує сенсор OV2640, автоматично визначає наявність зовнішньої PSRAM,
 * виділяє кадрові буфери та надає безпечний доступ до знімків.
 */
class PsramFrameBuffer {
public:
    // Стандартні піни для модуля AI-Thinker ESP32-CAM
    struct PinConfig {
        int pwdn     = 32;
        int reset    = -1;
        int xclk     = 0;
        int siod     = 26;
        int sioc     = 27;
        int y9       = 35;
        int y8       = 34;
        int y7       = 39;
        int y6       = 36;
        int y5       = 21;
        int y4       = 19;
        int y3       = 18;
        int y2       = 5;
        int vsync    = 25;
        int href     = 23;
        int pclk     = 22;
    };

    PsramFrameBuffer() = default;

    ~PsramFrameBuffer() {
        deinit();
    }

    PsramFrameBuffer(const PsramFrameBuffer&) = delete;
    PsramFrameBuffer& operator=(const PsramFrameBuffer&) = delete;

    /**
     * @brief Ініціалізує сенсор камери та виділяє буфери у PSRAM.
     * 
     * @param pins Налаштування GPIO виводів камери.
     * @param frameSize Бажана роздільна здатність (наприклад, FRAMESIZE_VGA).
     * @param jpegQuality Якість стиснення JPEG (від 10 до 63, менше — краще).
     * @return true у разі успішної ініціалізації, false при помилці.
     */
    bool begin(PinConfig pins = PinConfig{}, 
               framesize_t frameSize = FRAMESIZE_VGA, 
               int jpegQuality = 10) {
        
        hasPsram_ = psramFound();

        camera_config_t config = {};
        config.ledc_channel = LEDC_CHANNEL_1;
        config.ledc_timer   = LEDC_TIMER_1;
        config.pin_d0       = pins.y2;
        config.pin_d1       = pins.y3;
        config.pin_d2       = pins.y4;
        config.pin_d3       = pins.y5;
        config.pin_d4       = pins.y6;
        config.pin_d5       = pins.y7;
        config.pin_d6       = pins.y8;
        config.pin_d7       = pins.y9;
        config.pin_xclk     = pins.xclk;
        config.pin_pclk     = pins.pclk;
        config.pin_vsync    = pins.vsync;
        config.pin_href     = pins.href;
        config.pin_siod     = pins.siod;
        config.pin_sioc     = pins.sioc;
        config.pin_pwdn     = pins.pwdn;
        config.pin_reset    = pins.reset;
        config.xclk_freq_hz = 20000000;
        config.pixel_format = PIXFORMAT_JPEG;
        config.grab_mode    = CAMERA_GRAB_LATEST;

        // Налаштування використання PSRAM: якщо PSRAM доступна, використовуємо подвійну буферизацію
        if (hasPsram_) {
            config.frame_size   = frameSize;
            config.jpeg_quality = jpegQuality;
            config.fb_count     = 2;
            config.fb_location  = CAMERA_FB_IN_PSRAM;
        } else {
            // Без PSRAM обмежуємо роздільна здатність та кількість буферів для економії SRAM
            config.frame_size   = FRAMESIZE_SVGA;
            config.jpeg_quality = 12;
            config.fb_count     = 1;
            config.fb_location  = CAMERA_FB_IN_DRAM;
        }

        esp_err_t err = esp_camera_init(&config);
        if (err != ESP_OK) {
            isInitialized_ = false;
            return false;
        }

        // Оптимізація параметрів сенсора OV2640
        sensor_t* sensor = esp_camera_sensor_get();
        if (sensor != nullptr) {
            sensor->set_brightness(sensor, 0);     // -2 to 2
            sensor->set_contrast(sensor, 0);       // -2 to 2
            sensor->set_saturation(sensor, 0);     // -2 to 2
            sensor->set_whitebal(sensor, 1);       // 0 = disable , 1 = enable
            sensor->set_awb_gain(sensor, 1);       // 0 = disable , 1 = enable
            sensor->set_wb_mode(sensor, 0);        // 0 to 4
        }

        isInitialized_ = true;
        return true;
    }

    /**
     * @brief Захоплює один кадр із камери у вигляді RAII-об'єкта Frame.
     * @return Об'єкт Frame (якщо помилка, Frame::isValid() поверне false).
     */
    Frame acquireFrame() {
        if (!isInitialized_) {
            return Frame(nullptr);
        }
        camera_fb_t* fb = esp_camera_fb_get();
        return Frame(fb);
    }

    /**
     * @brief Звільняє ресурси камери.
     */
    void deinit() {
        if (isInitialized_) {
            esp_camera_deinit();
            isInitialized_ = false;
        }
    }

    /**
     * @brief Перевіряє, чи ініціалізовано модуль камери.
     */
    bool isInitialized() const {
        return isInitialized_;
    }

    /**
     * @brief Перевіряє, чи використовується пам'ять PSRAM.
     */
    bool isPsramAvailable() const {
        return hasPsram_;
    }

    /**
     * @brief Повертає кількість вільної пам'яті PSRAM у байтах.
     */
    size_t getFreePsram() const {
        return ESP.getFreePsram();
    }

    /**
     * @brief Повертає загальну кількість пам'яті PSRAM у байтах.
     */
    size_t getTotalPsram() const {
        return ESP.getPsramSize();
    }

private:
    bool isInitialized_{false};
    bool hasPsram_{false};
};

#endif // PSRAM_FRAME_BUFFER_HPP
