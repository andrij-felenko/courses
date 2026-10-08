#ifndef MJPEG_STREAMER_HPP
#define MJPEG_STREAMER_HPP

#include <esp_http_server.h>
#include <esp_err.h>
#include "ov2640_camera.hpp"

/**
 * @brief C++ клас для підняття HTTP-відеосервера та безперервної MJPEG-трансляції.
 * Реалізує відправку кадрового потоку у форматі multipart/x-mixed-replace.
 */
class MjpegStreamer {
public:
    MjpegStreamer() = default;
    ~MjpegStreamer();

    // Заборона копіювання об'єкта стримера
    MjpegStreamer(const MjpegStreamer&) = delete;
    MjpegStreamer& operator=(const MjpegStreamer&) = delete;

    /**
     * @brief Запуск HTTP-сервера на вказаному порту.
     * @param port Мережевий порт (наприклад, 80)
     * @param camera Посилання на ініціалізований об'єкт Ov2640Camera
     * @return ESP_OK у разі успішного запуску
     */
    esp_err_t start(uint16_t port, Ov2640Camera& camera);

    /**
     * @brief Зупинка HTTP-сервера та закриття відкритих з'єднань.
     */
    esp_err_t stop();

    [[nodiscard]] bool isStreaming() const noexcept { return server_ != nullptr; }

private:
    /**
     * @brief Статичний HTTP-обробник для маршруту /stream.
     */
    static esp_err_t streamHandler(httpd_req_t* req);

    httpd_handle_t server_ = nullptr;
    Ov2640Camera* camera_  = nullptr;
};

#endif // MJPEG_STREAMER_HPP
