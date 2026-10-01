#include "web_server.hpp"
#include "esp_log.h"
#include <cstring>
#include <cstdio>

static const char* TAG = "CameraWebServer";

#define PART_BOUNDARY "123456789000000000000987654321"
static const char* _STREAM_CONTENT_TYPE = "multipart/x-mixed-replace;boundary=" PART_BOUNDARY;
static const char* _STREAM_BOUNDARY = "\r\n--" PART_BOUNDARY "\r\n";
static const char* _STREAM_PART = "Content-Type: image/jpeg\r\nContent-Length: %u\r\n\r\n";

CameraWebServer::CameraWebServer(Ov3640Camera& camera) : camera_(camera) {}

CameraWebServer::~CameraWebServer() {
    stop();
}

esp_err_t CameraWebServer::start(uint16_t port) {
    httpd_config_t config = HTTPD_DEFAULT_CONFIG();
    config.server_port = port;

    esp_err_t ret = httpd_start(&server_handle_, &config);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Не вдалося запустити HTTP-сервер: 0x%x", ret);
        return ret;
    }

    httpd_uri_t stream_uri = {
        .uri       = "/stream",
        .method    = HTTP_GET,
        .handler   = streamHandler,
        .user_ctx  = &camera_
    };

    httpd_uri_t capture_uri = {
        .uri       = "/capture",
        .method    = HTTP_GET,
        .handler   = captureHandler,
        .user_ctx  = &camera_
    };

    httpd_register_uri_handler(server_handle_, &stream_uri);
    httpd_register_uri_handler(server_handle_, &capture_uri);

    ESP_LOGI(TAG, "Веб-сервер запущено на порту %d. Потік: /stream, Знімок: /capture", port);
    return ESP_OK;
}

void CameraWebServer::stop() {
    if (server_handle_) {
        httpd_stop(server_handle_);
        server_handle_ = nullptr;
        ESP_LOGI(TAG, "HTTP-сервер зупинено.");
    }
}

esp_err_t CameraWebServer::streamHandler(httpd_req_t* req) {
    auto* camera = static_cast<Ov3640Camera*>(req->user_ctx);
    char part_buf[128];

    esp_err_t res = httpd_resp_set_type(req, _STREAM_CONTENT_TYPE);
    if (res != ESP_OK) return res;

    ESP_LOGI(TAG, "Розпочато MJPEG стримінг.");

    while (true) {
        FrameBufferGuard fb_guard = camera->captureFrame();
        if (!fb_guard) {
            ESP_LOGE(TAG, "Не вдалося отримати кадр для відеопотоку.");
            res = ESP_FAIL;
            break;
        }

        res = httpd_resp_send_chunk(req, _STREAM_BOUNDARY, strlen(_STREAM_BOUNDARY));
        if (res == ESP_OK) {
            size_t hlen = snprintf(part_buf, sizeof(part_buf), _STREAM_PART, fb_guard->len);
            res = httpd_resp_send_chunk(req, part_buf, hlen);
        }
        if (res == ESP_OK) {
            res = httpd_resp_send_chunk(req, reinterpret_cast<const char*>(fb_guard->buf), fb_guard->len);
        }

        if (res != ESP_OK) break;
    }

    ESP_LOGI(TAG, "Завершено MJPEG стримінг.");
    return res;
}

esp_err_t CameraWebServer::captureHandler(httpd_req_t* req) {
    auto* camera = static_cast<Ov3640Camera*>(req->user_ctx);
    FrameBufferGuard fb_guard = camera->captureFrame();

    if (!fb_guard) {
        httpd_resp_send_500(req);
        return ESP_FAIL;
    }

    httpd_resp_set_type(req, "image/jpeg");
    httpd_resp_set_hdr(req, "Content-Disposition", "inline; filename=capture.jpg");
    return httpd_resp_send(req, reinterpret_cast<const char*>(fb_guard->buf), fb_guard->len);
}
