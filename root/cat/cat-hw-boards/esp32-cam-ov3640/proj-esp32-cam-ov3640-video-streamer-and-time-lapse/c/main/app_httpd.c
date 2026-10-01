#include "esp_http_server.h"
#include "esp_log.h"
#include "esp_camera.h"
#include <stdio.h>

static const char *TAG = "APP_HTTPD";

static esp_err_t mjpeg_stream_handler(httpd_req_t *req) {
    camera_fb_t *fb = NULL;
    esp_err_t res = ESP_OK;
    char part_buf[128];

    res = httpd_resp_set_type(req, "multipart/x-mixed-replace; boundary=frame_boundary");
    if (res != ESP_OK) {
        return res;
    }

    while (true) {
        fb = esp_camera_fb_get();
        if (!fb) {
            ESP_LOGE(TAG, "Помилка захоплення кадру камери");
            res = ESP_FAIL;
            break;
        }

        size_t hlen = snprintf(part_buf, sizeof(part_buf),
                               "\r\n--frame_boundary\r\n"
                               "Content-Type: image/jpeg\r\n"
                               "Content-Length: %zu\r\n\r\n",
                               fb->len);

        res = httpd_resp_send_chunk(req, part_buf, hlen);
        if (res == ESP_OK) {
            res = httpd_resp_send_chunk(req, (const char *)fb->buf, fb->len);
        }

        esp_camera_fb_return(fb);
        if (res != ESP_OK) {
            break;
        }
    }

    return res;
}

httpd_handle_t app_httpd_start_stream(void) {
    httpd_config_t config = HTTPD_DEFAULT_CONFIG();
    config.server_port = 80;

    httpd_handle_t server = NULL;
    if (httpd_start(&server, &config) == ESP_OK) {
        httpd_uri_t stream_uri = {
            .uri      = "/stream",
            .method   = HTTP_GET,
            .handler  = mjpeg_stream_handler,
            .user_ctx = NULL
        };
        httpd_register_uri_handler(server, &stream_uri);
        ESP_LOGI(TAG, "MJPEG HTTP стрімер запущено на порту 80 (/stream)");
    }
    return server;
}
