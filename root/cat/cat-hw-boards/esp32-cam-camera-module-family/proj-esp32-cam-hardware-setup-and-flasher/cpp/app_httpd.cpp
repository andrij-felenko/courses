#include "camera_config.hpp"
#include <esp_http_server.h>
#include <Arduino.h>

#define PART_BOUNDARY "123456789000000000000987654321"
static const char* STREAM_CONTENT_TYPE = "multipart/x-mixed-replace;boundary=" PART_BOUNDARY;
static const char* STREAM_BOUNDARY = "\r\n--" PART_BOUNDARY "\r\n";
static const char* STREAM_PART = "Content-Type: image/jpeg\r\nContent-Length: %u\r\n\r\n";

// Клас-обгортка для запуску HTTP-сервера відеостримінгу
class VideoStreamServer {
private:
    httpd_handle_t stream_httpd = nullptr;

    static esp_err_t stream_handler(httpd_req_t *req) {
        camera_fb_t *fb = nullptr;
        esp_err_t res = ESP_OK;
        char part_buf[64];

        res = httpd_resp_set_type(req, STREAM_CONTENT_TYPE);
        if (res != ESP_OK) return res;

        while (true) {
            fb = esp_camera_fb_get();
            if (!fb) {
                res = ESP_FAIL;
                break;
            }

            size_t hlen = snprintf(part_buf, sizeof(part_buf), STREAM_PART, fb->len);
            res = httpd_resp_send_chunk(req, part_buf, hlen);
            if (res == ESP_OK) {
                res = httpd_resp_send_chunk(req, (const char *)fb->buf, fb->len);
            }
            if (res == ESP_OK) {
                res = httpd_resp_send_chunk(req, STREAM_BOUNDARY, strlen(STREAM_BOUNDARY));
            }

            esp_camera_fb_return(fb);
            fb = nullptr;

            if (res != ESP_OK) break;
        }
        return res;
    }

public:
    VideoStreamServer() = default;

    bool start() {
        httpd_config_t config = HTTPD_DEFAULT_CONFIG();
        config.server_port = 80;

        httpd_uri_t stream_uri = {
            .uri       = "/stream",
            .method    = HTTP_GET,
            .handler   = stream_handler,
            .user_ctx  = nullptr
        };

        if (httpd_start(&stream_httpd, &config) == ESP_OK) {
            httpd_register_uri_handler(stream_httpd, &stream_uri);
            return true;
        }
        return false;
    }
};

static VideoStreamServer g_stream_server;

void start_video_server() {
    g_stream_server.start();
}
