#include "esp_http_server.h"
#include "esp_camera.h"
#include "esp_log.h"

static const char *TAG = "app_httpd";

#define PART_BOUNDARY "123456789000000000000987654321"
static const char* _STREAM_CONTENT_TYPE = "multipart/x-mixed-replace;boundary=" PART_BOUNDARY;
static const char* _STREAM_BOUNDARY = "\r\n--" PART_BOUNDARY "\r\n";
static const char* _STREAM_PART = "Content-Type: image/jpeg\r\nContent-Length: %u\r\n\r\n";

/**
 * @brief HTTP URI-обробник для трансляції MJPEG-відеопотоку /stream.
 */
static esp_err_t stream_handler(httpd_req_t *req)
{
    camera_fb_t *fb = NULL;
    esp_err_t res = ESP_OK;
    char part_buf[128];

    // Встановлюємо тип відповіді для MJPEG-потоку
    res = httpd_resp_set_type(req, _STREAM_CONTENT_TYPE);
    if (res != ESP_OK) {
        return res;
    }

    ESP_LOGI(TAG, "Новий клієнт підключився до відеопотоку /stream");

    while (true) {
        // Захоплення кадру з драйвера камери
        fb = esp_camera_fb_get();
        if (!fb) {
            ESP_LOGE(TAG, "Не вдалося отримати кадр із камери");
            res = ESP_FAIL;
            break;
        }

        // Відправка межі розбиття кадрів
        res = httpd_resp_send_chunk(req, _STREAM_BOUNDARY, strlen(_STREAM_BOUNDARY));
        if (res != ESP_OK) {
            esp_camera_fb_return(fb);
            break;
        }

        // Формування заголовка окремого JPEG-кадру
        int hlen = snprintf(part_buf, sizeof(part_buf), _STREAM_PART, fb->len);
        res = httpd_resp_send_chunk(req, part_buf, hlen);
        if (res != ESP_OK) {
            esp_camera_fb_return(fb);
            break;
        }

        // Передавання бінарного вмісту JPEG-зображення
        res = httpd_resp_send_chunk(req, (const char *)fb->buf, fb->len);

        // Обов'язкове повернення фреймбуфера драйверу для запобігання витокам пам'яті
        esp_camera_fb_return(fb);
        fb = NULL;

        if (res != ESP_OK) {
            break;
        }
    }

    ESP_LOGI(TAG, "Сесію потоку /stream завершено");
    return res;
}

/**
 * @brief Запуск HTTP-сервера потокового мовлення.
 */
esp_err_t app_httpd_start(void)
{
    httpd_config_t config = HTTPD_DEFAULT_CONFIG();
    config.server_port = 80;

    httpd_handle_t server = NULL;

    httpd_uri_t stream_uri = {
        .uri       = "/stream",
        .method    = HTTP_GET,
        .handler   = stream_handler,
        .user_ctx  = NULL
    };

    ESP_LOGI(TAG, "Запуск HTTP-сервера на порту %d", config.server_port);
    if (httpd_start(&server, &config) == ESP_OK) {
        httpd_register_uri_handler(server, &stream_uri);
        return ESP_OK;
    }

    ESP_LOGE(TAG, "Не вдалося запустити HTTP-сервер");
    return ESP_FAIL;
}
