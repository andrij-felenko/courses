#ifndef OV2640_CAMERA_HPP
#define OV2640_CAMERA_HPP

#include <esp_camera.h>
#include <esp_err.h>
#include <cstdint>
#include <utility>

/**
 * @brief Структура для конфігурації GPIO-виводів DVP-інтерфейсу та шини SCCB.
 * За замовчуванням використано розпіновку популярного модуля AI-Thinker ESP32-CAM.
 */
struct CameraPins {
    int pin_pwdn     = 32;  // Керування живленням (Power Down)
    int pin_reset    = -1;  // Апаратне скидання (-1, якщо не підключено)
    int pin_xclk     = 0;   // Тактовий сигнал генератора XCLK
    int pin_sscb_sda = 26;  // SCCB Дані (I2C SDA)
    int pin_sscb_scl = 27;  // SCCB Тактування (I2C SCL)

    // Линії паралельних даних DVP (D7 - D0)
    int pin_d7       = 35;
    int pin_d6       = 34;
    int pin_d5       = 39;
    int pin_d4       = 36;
    int pin_d3       = 21;
    int pin_d2       = 19;
    int pin_d1       = 18;
    int pin_d0       = 5;

    // Синхронізаційні сигнали DVP
    int pin_vsync    = 25;  // Кадрова синхронізація
    int pin_href     = 23;  // Рядкова синхронізація (Horizontal Reference)
    int pin_pclk     = 22;  // Піксельне тактування (Pixel Clock)
};

/**
 * @brief RAII-обгортка для автоматичного керування життєвим циклом кадрового буфера camera_fb_t.
 * Гарантує виклик esp_camera_fb_return() під час виходу з області видимості,
 * запобігаючи витокам оперативної пам'яті (PSRAM).
 */
class FrameBufferGuard {
public:
    explicit FrameBufferGuard(camera_fb_t* fb = nullptr) noexcept : fb_(fb) {}

    ~FrameBufferGuard() {
        reset();
    }

    // Заборона копіювання для запобігання подвійному звільненню буфера
    FrameBufferGuard(const FrameBufferGuard&) = delete;
    FrameBufferGuard& operator=(const FrameBufferGuard&) = delete;

    // Дозвіл переміщення (Move Semantics)
    FrameBufferGuard(FrameBufferGuard&& other) noexcept : fb_(other.fb_) {
        other.fb_ = nullptr;
    }

    FrameBufferGuard& operator=(FrameBufferGuard&& other) noexcept {
        if (this != &other) {
            reset();
            fb_ = other.fb_;
            other.fb_ = nullptr;
        }
        return *this;
    }

    void reset() noexcept {
        if (fb_ != nullptr) {
            esp_camera_fb_return(fb_);
            fb_ = nullptr;
        }
    }

    [[nodiscard]] camera_fb_t* get() const noexcept { return fb_; }
    [[nodiscard]] bool isValid() const noexcept { return fb_ != nullptr; }

    camera_fb_t* operator->() const noexcept { return fb_; }
    camera_fb_t& operator*() const noexcept { return *fb_; }

    [[nodiscard]] const uint8_t* data() const noexcept {
        return fb_ ? fb_->buf : nullptr;
    }

    [[nodiscard]] size_t size() const noexcept {
        return fb_ ? fb_->len : 0;
    }

    [[nodiscard]] camera_fb_t* release() noexcept {
        camera_fb_t* temp = fb_;
        fb_ = nullptr;
        return temp;
    }

private:
    camera_fb_t* fb_ = nullptr;
};

/**
 * @brief C++ клас для об'єктно-орієнтованого керування сенсором OV2640.
 * Включає конфігурацію DVP, SCCB, регістрів DSP/Sensor bank та роботу з PSRAM.
 */
class Ov2640Camera {
public:
    Ov2640Camera() = default;
    ~Ov2640Camera();

    // Заборона копіювання об'єкта камери
    Ov2640Camera(const Ov2640Camera&) = delete;
    Ov2640Camera& operator=(const Ov2640Camera&) = delete;

    /**
     * @brief Ініціалізація драйвера камери та регістрів OV2640.
     * @param pins Конструкція з номерами GPIO
     * @param frameSize Початкова роздільна здатність (наприклад, FRAMESIZE_VGA)
     * @param jpegQuality Якість JPEG (0-63, де менше значення означає вищу якість)
     * @return ESP_OK у разі успіху або відповідний код помилки
     */
    esp_err_t init(const CameraPins& pins = CameraPins{},
                   framesize_t frameSize = FRAMESIZE_VGA,
                   int jpegQuality = 12);

    /**
     * @brief Деініціалізація драйвера камери та звільнення ресурсів.
     */
    esp_err_t deinit();

    /**
     * @brief Захоплення нового кадру з виділенням RAII-обгортки.
     * @return FrameBufferGuard із покажчиком на кадр або порожній об'єкт при помилці.
     */
    FrameBufferGuard captureFrame();

    // Динамічна зміна параметрів сенсора
    esp_err_t setFrameSize(framesize_t size);
    esp_err_t setJpegQuality(int quality);
    esp_err_t setBrightness(int level);   // від -2 до 2
    esp_err_t setContrast(int level);     // від -2 до 2
    esp_err_t setSaturation(int level);   // від -2 до 2
    esp_err_t setFlip(bool hmirror, bool vflip);

    /**
     * @brief Низькорівневий запис у внутрішній регістр OV2640 із вибором регістрового банку.
     * @param bank Банк регістрів: 0x00 (DSP Bank) або 0x01 (Sensor Bank)
     * @param reg Адреса регістра
     * @param value Значення для запису
     */
    esp_err_t writeRegister(uint8_t bank, uint8_t reg, uint8_t value);

    [[nodiscard]] bool isInitialized() const noexcept { return initialized_; }

private:
    bool initialized_ = false;
    sensor_t* sensor_ = nullptr;
    camera_config_t config_{};
};

#endif // OV2640_CAMERA_HPP
