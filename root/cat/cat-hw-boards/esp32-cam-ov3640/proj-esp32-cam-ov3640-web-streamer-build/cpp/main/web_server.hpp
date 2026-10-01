#ifndef WEB_SERVER_HPP
#define WEB_SERVER_HPP

#include "esp_http_server.h"
#include "ov3640_camera.hpp"

/**
 * @brief Асинхронний C++ веб-сервер для MJPEG стримінгу та REST API керування
 */
class CameraWebServer {
public:
    explicit CameraWebServer(Ov3640Camera& camera);
    ~CameraWebServer();

    esp_err_t start(uint16_t port = 80);
    void stop();

private:
    Ov3640Camera& camera_;
    httpd_handle_t server_handle_{nullptr};

    static esp_err_t streamHandler(httpd_req_t* req);
    static esp_err_t captureHandler(httpd_req_t* req);
};

#endif // WEB_SERVER_HPP
