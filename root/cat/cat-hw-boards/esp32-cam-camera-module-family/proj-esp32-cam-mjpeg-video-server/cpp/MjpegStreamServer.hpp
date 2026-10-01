#ifndef MJPEG_STREAM_SERVER_HPP
#define MJPEG_STREAM_SERVER_HPP

#include <esp_http_server.h>
#include "esp_camera.h"
#include <memory>
#include <string_view>

// RAII-обгортка для автоматичного повернення фреймбуфера камери
class FrameBuffer {
public:
    explicit FrameBuffer(camera_fb_t* fb = nullptr) : fb_(fb) {}
    ~FrameBuffer() {
        if (fb_) {
            esp_camera_fb_return(fb_);
        }
    }

    // Заборона копіювання
    FrameBuffer(const FrameBuffer&) = delete;
    FrameBuffer& operator=(const FrameBuffer&) = delete;

    // Переміщення ресурсу
    FrameBuffer(FrameBuffer&& other) noexcept : fb_(other.fb_) {
        other.fb_ = nullptr;
    }
    FrameBuffer& operator=(FrameBuffer&& other) noexcept {
        if (this != &other) {
            if (fb_) esp_camera_fb_return(fb_);
            fb_ = other.fb_;
            other.fb_ = nullptr;
        }
        return *this;
    }

    [[nodiscard]] camera_fb_t* get() const noexcept { return fb_; }
    [[nodiscard]] bool valid() const noexcept { return fb_ != nullptr; }

private:
    camera_fb_t* fb_{nullptr};
};

// Клас MJPEG HTTP-відеосервера
class MjpegStreamServer {
public:
    MjpegStreamServer() = default;
    ~MjpegStreamServer();

    // Заборона копіювання
    MjpegStreamServer(const MjpegStreamServer&) = delete;
    MjpegStreamServer& operator=(const MjpegStreamServer&) = delete;

    // Ініціалізація камери та запуск сервера
    bool begin(uint16_t port = 80);
    void stop();

private:
    static esp_err_t streamHandler(httpd_req_t* req);

    httpd_handle_t serverHandle_{nullptr};
    bool isRunning_{false};
};

#endif // MJPEG_STREAM_SERVER_HPP
