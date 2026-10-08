#ifndef ESP32_CAMERA_WRAPPER_HPP
#define ESP32_CAMERA_WRAPPER_HPP

#include <Arduino.h>
#include <esp_camera.h>
#include <cstdint>
#include <utility>
#include <string>

/**
 * @brief Конфігураційна структура для налаштування DVP камери на ESP32-S3.
 */
struct CameraConfig {
    // Виводи інтерфейсу DVP для типової плати ESP32-S3-CAM / ESP32-S3-WROOM
    int pin_pwdn     = -1;
    int pin_reset    = -1;
    int pin_xclk     = 10;
    int pin_siod     = 40;
    int pin_sioc     = 39;
    int pin_d7       = 48;
    int pin_d6       = 11;
    int pin_d5       = 12;
    int pin_d4       = 14;
    int pin_d3       = 16;
    int pin_d2       = 18;
    int pin_d1       = 17;
    int pin_d0       = 15;
    int pin_vsync    = 38;
    int pin_href     = 47;
    int pin_pclk     = 13;

    // Параметри тактування та обробки
    int xclk_freq_hz        = 20000000;
    pixformat_t pixel_format = PIXFORMAT_JPEG;
    framesize_t frame_size   = FRAMESIZE_VGA;
    int jpeg_quality         = 12; // 1 (найвища якість) - 63 (найнижча)
    size_t fb_count          = 2;  // Подвійна буферизація в PSRAM
    camera_grab_mode_t grab_mode = CAMERA_GRAB_WHEN_EMPTY;
    camera_fb_location_t fb_location = CAMERA_FB_IN_PSRAM;

    /**
     * @brief Перетворення внутрішніх параметрів у структуру esp-camera C API.
     */
    camera_config_t toEspCameraConfig() const;
};

/**
 * @brief RAII-обгортка для управління життєвим циклом кадрового буфера camera_fb_t.
 * Гарантує виклик esp_camera_fb_return у деструкторі, запобігаючи витокам пам'яті в PSRAM.
 */
class FrameBufferGuard {
public:
    explicit FrameBufferGuard(camera_fb_t* fb = nullptr) noexcept;
    ~FrameBufferGuard();

    // Заборона копіювання для запобігання подвійному звільненню
    FrameBufferGuard(const FrameBufferGuard&) = delete;
    FrameBufferGuard& operator=(const FrameBufferGuard&) = delete;

    // Переміщення власності
    FrameBufferGuard(FrameBufferGuard&& other) noexcept;
    FrameBufferGuard& operator=(FrameBufferGuard&& other) noexcept;

    void reset(camera_fb_t* new_fb = nullptr) noexcept;
    camera_fb_t* release() noexcept;

    [[nodiscard]] camera_fb_t* get() const noexcept { return fb_; }
    [[nodiscard]] const uint8_t* data() const noexcept { return fb_ ? fb_->buf : nullptr; }
    [[nodiscard]] size_t size() const noexcept { return fb_ ? fb_->len : 0; }
    [[nodiscard]] size_t width() const noexcept { return fb_ ? fb_->width : 0; }
    [[nodiscard]] size_t height() const noexcept { return fb_ ? fb_->height : 0; }
    [[nodiscard]] pixformat_t format() const noexcept { return fb_ ? fb_->format : PIXFORMAT_RAW; }
    [[nodiscard]] bool valid() const noexcept { return fb_ != nullptr; }

    explicit operator bool() const noexcept { return valid(); }
    camera_fb_t* operator->() const noexcept { return fb_; }

private:
    camera_fb_t* fb_{nullptr};
};

/**
 * @brief C++ клас-обгортка над драйвером esp_camera для контролера ESP32-S3.
 */
class Esp32CameraWrapper {
public:
    Esp32CameraWrapper() = default;
    ~Esp32CameraWrapper();

    // Заборона копіювання екземпляра драйвера камери
    Esp32CameraWrapper(const Esp32CameraWrapper&) = delete;
    Esp32CameraWrapper& operator=(const Esp32CameraWrapper&) = delete;

    /**
     * @brief Ініціалізація камери та перевірка PSRAM.
     */
    bool init(const CameraConfig& config = CameraConfig());

    /**
     * @brief Деініціалізація драйвера камери.
     */
    bool deinit();

    /**
     * @brief Захоплення нового кадру із поверненням RAII-обгортки.
     */
    [[nodiscard]] FrameBufferGuard captureFrame();

    // Методи динамічного налаштування сенсора
    bool setFrameSize(framesize_t size);
    bool setJpegQuality(int quality);
    bool setBrightness(int brightness);
    bool setContrast(int contrast);
    bool setSaturation(int saturation);
    bool setVFlip(bool enable);
    bool setHMirror(bool enable);

    [[nodiscard]] bool isInitialized() const noexcept { return initialized_; }
    [[nodiscard]] const CameraConfig& getConfig() const noexcept { return config_; }
    [[nodiscard]] sensor_t* getSensor() const noexcept;

private:
    CameraConfig config_;
    bool initialized_{false};
};

#endif // ESP32_CAMERA_WRAPPER_HPP
