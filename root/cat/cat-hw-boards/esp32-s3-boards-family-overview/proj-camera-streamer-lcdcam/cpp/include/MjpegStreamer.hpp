#ifndef MJPEG_STREAMER_HPP
#define MJPEG_STREAMER_HPP

#include <atomic>
#include "esp_err.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/queue.h"
#include "FrameServer.hpp"

namespace camera {

/**
 * @brief Потоковий мережевий MJPEG-передавач по Wi-Fi.
 * 
 * Отримує кадри з FrameServer та передає їх асинхронним HTTP-клієнтам
 * у форматі multipart/x-mixed-replace.
 */
class MjpegStreamer {
public:
    explicit MjpegStreamer(uint16_t port = 8080);
    ~MjpegStreamer();

    // Некопійований об'єкт
    MjpegStreamer(const MjpegStreamer&) = delete;
    MjpegStreamer& operator=(const MjpegStreamer&) = delete;

    /**
     * @brief Запуск задач MJPEG серверу.
     */
    esp_err_t start(FrameServer& server, UBaseType_t priority = 4, uint32_t stackSize = 8192);

    /**
     * @brief Зупинка стримера.
     */
    esp_err_t stop();

    /// @brief Задействований мережевий порт
    uint16_t port() const { return port_; }

    /// @brief Перевірка статусу запуску
    bool isRunning() const { return running_; }

    /// @brief Кількість підключених активних клієнтів
    size_t activeClients() const { return activeClients_.load(); }

private:
    static void streamerTask(void* arg);
    void runServer();
    void sendMjpegFrame(int socketFd, const FrameBuffer::Ptr& frame);

    FrameServer* server_{nullptr};
    QueueHandle_t frameQueue_{nullptr};
    TaskHandle_t taskHandle_{nullptr};
    uint16_t port_;
    std::atomic<bool> running_{false};
    std::atomic<size_t> activeClients_{0};
};

} // namespace camera

#endif // MJPEG_STREAMER_HPP
