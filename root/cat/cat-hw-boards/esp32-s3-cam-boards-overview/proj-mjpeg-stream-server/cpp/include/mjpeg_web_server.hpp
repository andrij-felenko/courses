#ifndef MJPEG_WEB_SERVER_HPP
#define MJPEG_WEB_SERVER_HPP

#include <WiFi.h>
#include <ESPAsyncWebServer.h>
#include <ArduinoJson.h>
#include <atomic>
#include <memory>

#include "esp32_camera_wrapper.hpp"

/**
 * @brief Неблокуючий мережевий сервер для трансляції MJPEG-відео через HTTP
 * та інтерактивної взаємодії / потокової передачі через WebSocket.
 */
class MjpegWebServer {
public:
    explicit MjpegWebServer(Esp32CameraWrapper& camera, uint16_t port = 80);
    ~MjpegWebServer();

    MjpegWebServer(const MjpegWebServer&) = delete;
    MjpegWebServer& operator=(const MjpegWebServer&) = delete;

    /**
     * @brief Запуск HTTP та WebSocket сервера.
     */
    bool begin();

    /**
     * @brief Зупинка веб-сервера.
     */
    void stop();

    /**
     * @brief Періодичне обслуговування WebSocket розсилки відеокадрів.
     * Викликається у циклі loop().
     */
    void update();

    [[nodiscard]] uint32_t getActiveWsClients() const noexcept { return ws_client_count_.load(); }
    [[nodiscard]] bool isRunning() const noexcept { return running_; }

private:
    void setupRoutes();
    void handleRoot(AsyncWebServerRequest* request);
    void handleMjpegStream(AsyncWebServerRequest* request);

    void onWebSocketEvent(AsyncWebSocket* server, AsyncWebSocketClient* client,
                        AwsEventType type, void* arg, uint8_t* data, size_t len);
    void processWebSocketCommand(AsyncWebSocketClient* client, uint8_t* data, size_t len);
    void sendStatusJson(AsyncWebSocketClient* client);

    Esp32CameraWrapper& camera_;
    uint16_t port_;
    AsyncWebServer server_;
    AsyncWebSocket ws_;

    bool running_{false};
    std::atomic<uint32_t> ws_client_count_{0};
    uint32_t frame_interval_ms_{40}; // ~25 FPS для WebSocket потоку
    uint32_t last_frame_time_ms_{0};
};

#endif // MJPEG_WEB_SERVER_HPP
