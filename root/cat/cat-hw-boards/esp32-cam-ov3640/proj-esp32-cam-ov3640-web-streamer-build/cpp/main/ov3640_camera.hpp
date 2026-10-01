#ifndef OV3640_CAMERA_HPP
#define OV3640_CAMERA_HPP

#include "esp_camera.h"
#include "esp_err.h"
#include <memory>

/**
 * @brief RAII-обгортка для автоматичного управління системним кадровим буфером camera_fb_t
 */
class FrameBufferGuard {
public:
    explicit FrameBufferGuard(camera_fb_t* fb = nullptr) : fb_(fb) {}
    ~FrameBufferGuard() {
        if (fb_) {
            esp_camera_fb_return(fb_);
        }
    }

    // Заборона копіювання
    FrameBufferGuard(const FrameBufferGuard&) = delete;
    FrameBufferGuard& operator=(const FrameBufferGuard&) = delete;

    // Дозвіл переміщення
    FrameBufferGuard(FrameBufferGuard&& other) noexcept : fb_(other.fb_) {
        other.fb_ = nullptr;
    }
    FrameBufferGuard& operator=(FrameBufferGuard&& other) noexcept {
        if (this != &other) {
            if (fb_) esp_camera_fb_return(fb_);
            fb_ = other.fb_;
            other.fb_ = nullptr;
        }
        return *this;
    }

    camera_fb_t* get() const { return fb_; }
    camera_fb_t* operator->() const { return fb_; }
    explicit operator bool() const { return fb_ != nullptr; }

private:
    camera_fb_t* fb_{nullptr};
};

/**
 * @brief Клас для ініціалізації та управління параметрами матриці OV3640
 */
class Ov3640Camera {
public:
    Ov3640Camera() = default;
    ~Ov3640Camera();

    // Ініціалізація драйвера камери
    esp_err_t init();

    // Отримання кадрового буфера із збереженням RAII-безпеки
    FrameBufferGuard captureFrame();

    // REST API керування параметрами
    esp_err_t setFramesize(framesize_t size);
    esp_err_t setBrightness(int level);

private:
    bool initialized_{false};
    camera_config_t config_{};
    void setupPinConfig();
};

#endif // OV3640_CAMERA_HPP
