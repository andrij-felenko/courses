#pragma once

#include "esp_camera.h"
#include "esp_err.h"
#include <cstddef>
#include <cstdint>
#include <span>

namespace esp32_cam {

// RAII-обгортка над буфером кадру camera_fb_t для автоматичного звільнення ресурсу через esp_camera_fb_return()
class FrameBuffer {
public:
    explicit FrameBuffer(camera_fb_t* fb = nullptr) noexcept;
    ~FrameBuffer();

    // Заборона копіювання для уникнення подвійного звільнення буфера
    FrameBuffer(const FrameBuffer&) = delete;
    FrameBuffer& operator=(const FrameBuffer&) = delete;

    // Переміщення ресурсу
    FrameBuffer(FrameBuffer&& other) noexcept;
    FrameBuffer& operator=(FrameBuffer&& other) noexcept;

    [[nodiscard]] bool valid() const noexcept { return fb_ != nullptr; }
    [[nodiscard]] explicit operator bool() const noexcept { return valid(); }

    [[nodiscard]] const camera_fb_t* get() const noexcept { return fb_; }
    [[nodiscard]] size_t size() const noexcept { return fb_ ? fb_->len : 0; }
    [[nodiscard]] int width() const noexcept { return fb_ ? fb_->width : 0; }
    [[nodiscard]] int height() const noexcept { return fb_ ? fb_->height : 0; }
    [[nodiscard]] pixformat_t format() const noexcept { return fb_ ? fb_->format : PIXFORMAT_RAW; }

    [[nodiscard]] std::span<const uint8_t> data() const noexcept {
        if (!fb_ || !fb_->buf) {
            return {};
        }
        return {fb_->buf, fb_->len};
    }

    // Ручне звільнення буфера (якщо потрібно до знищення об'єкта)
    void release() noexcept;

private:
    camera_fb_t* fb_{nullptr};
};

// Клас інкапсуляції конфігурації, запуску драйвера камери та захоплення кадрів
class CameraManager {
public:
    CameraManager() = default;
    ~CameraManager();

    CameraManager(const CameraManager&) = delete;
    CameraManager& operator=(const CameraManager&) = delete;

    // Ініціалізація драйвера камери з налаштуванням GPIO та перевіркою PSRAM
    [[nodiscard]] esp_err_t init() noexcept;

    // Захоплення кадру у формі RAII-об'єкта FrameBuffer
    [[nodiscard]] FrameBuffer capture_frame() noexcept;

    [[nodiscard]] bool is_initialized() const noexcept { return initialized_; }

private:
    bool initialized_{false};
    camera_config_t make_default_config() const noexcept;
};

} // namespace esp32_cam
