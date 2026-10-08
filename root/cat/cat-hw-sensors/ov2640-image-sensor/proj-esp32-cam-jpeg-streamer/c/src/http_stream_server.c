#include "http_stream_server.h"
#include "app_camera.h"
#include "esp_log.h"
#include "esp_camera.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include <stdio.h>

static const char *TAG = "http_stream_server";
static httpd_handle_t s_stream_httpd = NULL;

/**
 * @brief HTTP-обробник асинхронної потокової трансляції MJPEG (маршрут /stream).
 *
 * Виконує неблокуючий цикл захоплення кадрів з драйвера камери через esp_camera_fb_get(),
 * формує заголовки multipart/x-mixed-replace та відправляє JPEG-дані частинами (chunks).
 * Після кожного кадру обов'язково викликається esp_camera_fb_return() для вивільнення PSRAM.
 */
static esp_err_t stream_uri_handler(httpd_req_t *req) {
    camera_fb_t *fb = NULL;
    esp_err_t res = ESP_OK;
    char part_buf[128];
    int64_t last_frame_time = esp_timer_get_time();

    res = httpd_resp_set_type(req, STREAM_CONTENT_TYPE);
    if (res != ESP_OK) {
        ESP_LOGE(TAG, "Не вдалося встановити заголовок Content-Type: %d", res);
        return res;
    }

    httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
    httpd_resp_set_hdr(req, "X-Framerate", "60");

    ESP_LOGI(TAG, "Розпочато відеопотік для HTTP-клієнта");

    while (true) {
        fb = esp_camera_fb_get();
        if (!fb) {
            ESP_LOGE(TAG, "Помилка захоплення кадру з OV2640");
            res = ESP_FAIL;
            break;
        }

        size_t _jpg_buf_len = fb->len;
        size_t hlen = snprintf(part_buf, sizeof(part_buf),
                               "\r\n--%s\r\nContent-Type: image/jpeg\r\nContent-Length: %zu\r\n\r\n",
                               STREAM_PART_BOUNDARY, _jpg_buf_len);

        res = httpd_resp_send_chunk(req, part_buf, hlen);
        if (res == ESP_OK) {
            res = httpd_resp_send_chunk(req, (const char *)fb->buf, _jpg_buf_len);
        }

        /* Обов'язкове повернення кадрового буфера в драйвер! */
        esp_camera_fb_return(fb);
        fb = NULL;

        if (res != ESP_OK) {
            ESP_LOGW(TAG, "Перервано передачу даних клієнту (з'єднання закрито)");
            break;
        }

        int64_t frame_time = esp_timer_get_time() - last_frame_time;
        last_frame_time = esp_timer_get_time();
        int fps = (int)(1000000 / (frame_time > 0 ? frame_time : 1));
        ESP_LOGD(TAG, "Кадр відправлено: %zu байт, FPS: %d", _jpg_buf_len, fps);

        /* Короткий відпочинок для запобігання голодуванню watchdog та інших задач */
        vTaskDelay(pdMS_TO_TICKS(1));
    }

    ESP_LOGI(TAG, "Завершено відеопотік HTTP-клієнта");
    return res;
}

esp_err_t http_stream_server_start(void) {
    if (s_stream_httpd != NULL) {
        ESP_LOGW(TAG, "HTTP-сервер вже запущено");
        return ESP_OK;
    }

    httpd_config_t config = HTTPD_DEFAULT_CONFIG();
    config.server_port = STREAM_SERVER_PORT;
    config.ctrl_port = 32768;
    config.max_open_sockets = 4;
    config.lru_purge_enable = true;

    httpd_uri_t stream_uri = {
        .uri       = "/stream",
        .method    = HTTP_GET,
        .handler   = stream_uri_handler,
        .user_ctx  = NULL
    };

    ESP_LOGI(TAG, "Запуск HTTP-сервера на порту %d...", config.server_port);
    esp_err_t ret = httpd_start(&s_stream_httpd, &config);
    if (ret == ESP_OK) {
        httpd_register_uri_handler(s_stream_httpd, &stream_uri);
        ESP_LOGI(TAG, "Сервер потокового відео успішно запущено. URI: /stream");
    } else {
        ESP_LOGE(TAG, "Помилка запуску HTTP-сервера: 0x%x", ret);
    }

    return ret;
}

esp_err_t http_stream_server_stop(void) {
    if (s_stream_httpd == NULL) {
        return ESP_OK;
    }

    esp_err_t ret = httpd_stop(s_stream_httpd);
    if (ret == ESP_OK) {
        s_stream_httpd = NULL;
        ESP_LOGI(TAG, "HTTP-сервер зупинено");
    }
    return ret;
}

httpd_handle_t http_stream_server_get_handle(void) {
    return s_stream_httpd;
}
