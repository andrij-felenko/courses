#ifndef VIDEO_STREAMER_HPP
#define VIDEO_STREAMER_HPP

#include "esp_http_server.h"
#include "esp_camera.h"

// Клас веб-сервера для трансляції відеопотоку MJPEG та налаштування параметрів камери.
class VideoStreamer {
public:
    VideoStreamer();
    ~VideoStreamer();

    // Запускає веб-сервер на вказаному порту.
    bool start(uint16_t port = 80);

    // Зупиняє роботу сервера.
    void stop();

private:
    static esp_err_t streamHandler(httpd_req_t* req);
    httpd_handle_t m_serverHandle;
};

#endif // VIDEO_STREAMER_HPP
