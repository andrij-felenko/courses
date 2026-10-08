#include "mjpeg_server.h"
#include "ov2640_driver.h"
#include "esp_log.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include <stdio.h>
#include <string.h>

static const char *TAG = "mjpeg_server";

static esp_err_t stream_handler(httpd_req_t *req) {
    camera_fb_t *fb = NULL;
    esp_err_t res = ESP_OK;
    char part_header[128];
    uint32_t frame_count = 0;
    int64_t last_frame_time = esp_timer_get_time();

    ESP_LOGI(TAG, "Клієнт підключився до MJPEG відеопотоку /stream");

    res = httpd_resp_set_type(req, "multipart/x-mixed-replace; boundary=" MJPEG_STREAM_BOUNDARY);
    if (res != ESP_OK) {
        ESP_LOGE(TAG, "Помилка встановлення заголовку Content-Type: %d", res);
        return res;
    }

    httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
    httpd_resp_set_hdr(req, "Cache-Control", "no-cache, private, max-age=0, must-revalidate");
    httpd_resp_set_hdr(req, "Pragma", "no-cache");

    while (true) {
        fb = ov2640_get_frame(3000);
        if (!fb) {
            ESP_LOGW(TAG, "Таймаут отримання кадру з драйвера камери");
            res = ESP_FAIL;
            break;
        }

        size_t hlen = snprintf(part_header, sizeof(part_header),
                               "\r\n--" MJPEG_STREAM_BOUNDARY "\r\n"
                               "Content-Type: image/jpeg\r\n"
                               "Content-Length: %u\r\n\r\n",
                               (unsigned int)fb->len);

        res = httpd_resp_send_chunk(req, part_header, hlen);
        if (res == ESP_OK) {
            res = httpd_resp_send_chunk(req, (const char *)fb->buf, fb->len);
        }

        ov2640_return_frame(fb);
        fb = NULL;

        if (res != ESP_OK) {
            ESP_LOGI(TAG, "Клієнт відключився від відеопотоку (код: %d)", res);
            break;
        }

        frame_count++;
        int64_t now = esp_timer_get_time();
        if (now - last_frame_time >= 5000000) {
            float fps = (float)frame_count * 1000000.0f / (float)(now - last_frame_time);
            ESP_LOGI(TAG, "Поточна швидкість MJPEG трансляції: %.2f FPS", fps);
            frame_count = 0;
            last_frame_time = now;
        }

        vTaskDelay(pdMS_TO_TICKS(10));
    }

    return res;
}

httpd_handle_t mjpeg_server_start(void) {
    httpd_config_t config = HTTPD_DEFAULT_CONFIG();
    config.server_port = MJPEG_SERVER_PORT;
    config.ctrl_port = 32768;
    config.max_open_sockets = 4;
    config.backlog_conn = 4;
    config.lru_purge_enable = true;

    httpd_handle_t server = NULL;
    ESP_LOGI(TAG, "Запуск HTTP-сервера на порту %d...", config.server_port);

    if (httpd_start(&server, &config) == ESP_OK) {
        httpd_uri_t stream_uri = {
            .uri       = MJPEG_URI_STREAM,
            .method    = HTTP_GET,
            .handler   = stream_handler,
            .user_ctx  = NULL
        };
        httpd_register_uri_handler(server, &stream_uri);
        ESP_LOGI(TAG, "HTTP-сервер успішно запущено. URI трансляції: http://<IP-адреса>/stream");
        return server;
    }

    ESP_LOGE(TAG, "Не вдалося запустити HTTP-сервер");
    return NULL;
}

esp_err_t mjpeg_server_stop(httpd_handle_t server) {
    if (server) {
        esp_err_t err = httpd_stop(server);
        if (err == ESP_OK) {
            ESP_LOGI(TAG, "HTTP-сервер зупинено");
        }
        return err;
    }
    return ESP_OK;
}
