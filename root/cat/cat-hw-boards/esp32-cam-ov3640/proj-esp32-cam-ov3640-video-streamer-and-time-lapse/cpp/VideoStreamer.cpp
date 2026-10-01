#include "VideoStreamer.hpp"
#include <Arduino.h>

#define PART_BOUNDARY "123456789000000000000987654321"
static const char* STREAM_CONTENT_TYPE = "multipart/x-mixed-replace;boundary=" PART_BOUNDARY;
static const char* STREAM_BOUNDARY = "\r\n--" PART_BOUNDARY "\r\n";
static const char* STREAM_PART = "Content-Type: image/jpeg\r\nContent-Length: %u\r\n\r\n";

VideoStreamer::VideoStreamer() : m_serverHandle(nullptr) {}

VideoStreamer::~VideoStreamer() {
    stop();
}

bool VideoStreamer::start(uint16_t port) {
    httpd_config_t config = HTTPD_DEFAULT_CONFIG();
    config.server_port = port;

    httpd_uri_t streamUri = {
        .uri      = "/stream",
        .method   = HTTP_GET,
        .handler  = VideoStreamer::streamHandler,
        .user_ctx = nullptr
    };

    if (httpd_start(&m_serverHandle, &config) == ESP_OK) {
        httpd_register_uri_handler(m_serverHandle, &streamUri);
        return true;
    }
    return false;
}

void VideoStreamer::stop() {
    if (m_serverHandle != nullptr) {
        httpd_stop(m_serverHandle);
        m_serverHandle = nullptr;
    }
}

esp_err_t VideoStreamer::streamHandler(httpd_req_t* req) {
    camera_fb_t* fb = nullptr;
    esp_err_t res = ESP_OK;
    char partBuf[64];

    res = httpd_resp_set_type(req, STREAM_CONTENT_TYPE);
    if (res != ESP_OK) {
        return res;
    }

    while (true) {
        fb = esp_camera_fb_get();
        if (!fb) {
            res = ESP_FAIL;
            break;
        }

        res = httpd_resp_send_chunk(req, STREAM_BOUNDARY, strlen(STREAM_BOUNDARY));
        if (res == ESP_OK) {
            std::size_t hlen = std::snprintf(partBuf, sizeof(partBuf), STREAM_PART, fb->len);
            res = httpd_resp_send_chunk(req, partBuf, hlen);
        }
        if (res == ESP_OK) {
            res = httpd_resp_send_chunk(req, (const char*)fb->buf, fb->len);
        }

        esp_camera_fb_return(fb);
        fb = nullptr;

        if (res != ESP_OK) {
            break;
        }
    }

    return res;
}
