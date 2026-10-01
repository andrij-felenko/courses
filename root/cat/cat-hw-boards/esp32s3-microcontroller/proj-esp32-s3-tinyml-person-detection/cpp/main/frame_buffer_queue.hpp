#ifndef FRAME_BUFFER_QUEUE_HPP
#define FRAME_BUFFER_QUEUE_HPP

#include <esp_camera.h>
#include <esp_log.h>
#include <freertos/FreeRTOS.h>
#include <freertos/queue.h>
#include <memory>

namespace esp32s3 {

// RAII обгортка для автоматичного повернення буфера камери у драйвер
class ScopedFrame {
public:
    explicit ScopedFrame(camera_fb_t* fb = nullptr) : fb_(fb) {}

    ~ScopedFrame() {
        reset();
    }

    ScopedFrame(const ScopedFrame&) = delete;
    ScopedFrame& operator=(const ScopedFrame&) = delete;

    ScopedFrame(ScopedFrame&& other) noexcept : fb_(other.fb_) {
        other.fb_ = nullptr;
    }

    ScopedFrame& operator=(ScopedFrame&& other) noexcept {
        if (this != &other) {
            reset();
            fb_ = other.fb_;
            other.fb_ = nullptr;
        }
        return *this;
    }

    void reset(camera_fb_t* fb = nullptr) {
        if (fb_) {
            esp_camera_fb_return(fb_);
        }
        fb_ = fb;
    }

    [[nodiscard]] camera_fb_t* get() const { return fb_; }
    [[nodiscard]] const uint8_t* data() const { return fb_ ? fb_->buf : nullptr; }
    [[nodiscard]] size_t size() const { return fb_ ? fb_->len : 0; }
    [[nodiscard]] bool valid() const { return fb_ != nullptr; }

    camera_fb_t* release() {
        camera_fb_t* temp = fb_;
        fb_ = nullptr;
        return temp;
    }

private:
    camera_fb_t* fb_{nullptr};
};

// Потокобезпечна черга FreeRTOS для передачі вказівників на кадрові буфери
class FrameBufferQueue {
public:
    explicit FrameBufferQueue(size_t queue_depth = 2) {
        queue_handle_ = xQueueCreate(queue_depth, sizeof(camera_fb_t*));
    }

    ~FrameBufferQueue() {
        if (queue_handle_) {
            camera_fb_t* fb = nullptr;
            while (xQueueReceive(queue_handle_, &fb, 0) == pdTRUE) {
                if (fb) {
                    esp_camera_fb_return(fb);
                }
            }
            vQueueDelete(queue_handle_);
        }
    }

    bool push(camera_fb_t* fb, TickType_t wait_ticks = 0) {
        if (!queue_handle_ || !fb) return false;
        if (xQueueSend(queue_handle_, &fb, wait_ticks) != pdTRUE) {
            ESP_LOGW(TAG, "Переповнення черги кадрових буферів. Кадрів скинуто");
            esp_camera_fb_return(fb); // Скидаємо кадр, якщо черга заповнена
            return false;
        }
        return true;
    }

    ScopedFrame pop(TickType_t wait_ticks = portMAX_DELAY) {
        if (!queue_handle_) return ScopedFrame(nullptr);
        camera_fb_t* fb = nullptr;
        if (xQueueReceive(queue_handle_, &fb, wait_ticks) == pdTRUE) {
            return ScopedFrame(fb);
        }
        return ScopedFrame(nullptr);
    }

private:
    static constexpr const char* TAG = "FrameBufferQueue";
    QueueHandle_t queue_handle_{nullptr};
};

} // namespace esp32s3

#endif // FRAME_BUFFER_QUEUE_HPP
