#include "mjpeg_stream_server.h"
#include "camera_driver.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include <stdio.h>

static const char *TAG = "MJPEG_SERVER";

static esp_err_t stream_uri_handler(httpd_req_t *req)
{
    esp_camera_fb_t *fb = NULL;
    esp_err_t res = ESP_OK;
    char part_buf[128];

    res = httpd_resp_set_type(req, STREAM_CONTENT_TYPE);
    if (res != ESP_OK) {
        ESP_LOGE(TAG, "Не вдалося встановити заголовки HTTP Content-Type");
        return res;
    }

    httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
    httpd_resp_set_hdr(req, "X-Framerate", "30");

    ESP_LOGI(TAG, "Нове підключення клієнта до MJPEG-потоку /stream");

    while (true) {
        fb = camera_driver_capture_frame();
        if (!fb) {
            ESP_LOGE(TAG, "Помилка захоплення кадру з камери");
            res = ESP_FAIL;
            break;
        }

        size_t hlen = snprintf(part_buf, sizeof(part_buf),
                               "\r\n--" STREAM_BOUNDARY "\r\n"
                               "Content-Type: image/jpeg\r\n"
                               "Content-Length: %u\r\n\r\n",
                               (unsigned int)fb->len);

        res = httpd_resp_send_chunk(req, part_buf, hlen);
        if (res == ESP_OK) {
            res = httpd_resp_send_chunk(req, (const char *)fb->buf, fb->len);
        }

        camera_driver_return_frame(fb);
        fb = NULL;

        if (res != ESP_OK) {
            ESP_LOGI(TAG, "Клієнт відключився від відеопотоку");
            break;
        }

        vTaskDelay(pdMS_TO_TICKS(10));
    }

    return res;
}

esp_err_t mjpeg_stream_server_start(httpd_handle_t *server_handle)
{
    if (server_handle == NULL) {
        return ESP_ERR_INVALID_ARG;
    }

    httpd_config_t config = HTTPD_DEFAULT_CONFIG();
    config.server_port = HTTP_STREAM_PORT;
    config.ctrl_port = 5000;
    config.max_open_sockets = 7;
    config.lru_purge_enable = true;

    ESP_LOGI(TAG, "Запуск HTTP-сервера на порту %d...", config.server_port);

    esp_err_t err = httpd_start(server_handle, &config);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Не вдалося запустити HTTP-сервер: %s", esp_err_to_name(err));
        return err;
    }

    httpd_uri_t stream_uri = {
        .uri       = "/stream",
        .method    = HTTP_GET,
        .handler   = stream_uri_handler,
        .user_ctx  = NULL
    };

    err = httpd_register_uri_handler(*server_handle, &stream_uri);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Не вдалося зареєструвати URI-хендлер /stream: %s", esp_err_to_name(err));
        httpd_stop(*server_handle);
        *server_handle = NULL;
        return err;
    }

    ESP_LOGI(TAG, "HTTP-сервер MJPEG успішно запущено. Шлях: /stream");
    return ESP_OK;
}

esp_err_t mjpeg_stream_server_stop(httpd_handle_t server_handle)
{
    if (server_handle == NULL) {
        return ESP_ERR_INVALID_ARG;
    }

    esp_err_t err = httpd_stop(server_handle);
    if (err == ESP_OK) {
        ESP_LOGI(TAG, "HTTP-сервер зупинено.");
    } else {
        ESP_LOGE(TAG, "Помилка зупинки HTTP-сервера: %s", esp_err_to_name(err));
    }
    return err;
}
