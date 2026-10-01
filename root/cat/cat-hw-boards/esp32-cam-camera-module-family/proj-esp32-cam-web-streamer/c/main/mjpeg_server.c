#include "mjpeg_server.h"
#include "esp_camera.h"
#include "esp_http_server.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

static const char *TAG = "mjpeg_server";

#define PART_BOUNDARY "123456789000000000000987654321"
static const char *_STREAM_CONTENT_TYPE = "multipart/x-mixed-replace;boundary=" PART_BOUNDARY;
static const char *_STREAM_BOUNDARY = "\r\n--" PART_BOUNDARY "\r\n";
static const char *_STREAM_PART = "Content-Type: image/jpeg\r\nContent-Length: %u\r\n\r\n";

static httpd_handle_t stream_httpd = NULL;

// Обработник HTTP-запиту потокового відео MJPEG
static esp_err_t stream_handler(httpd_req_t *req)
{
    camera_fb_t *fb = NULL;
    esp_err_t res = ESP_OK;
    size_t _jpg_buf_len = 0;
    uint8_t *_jpg_buf = NULL;
    char part_buf[128];

    // Встановлення HTTP-заголовка для мультипарт-потоку
    res = httpd_resp_set_type(req, _STREAM_CONTENT_TYPE);
    if (res != ESP_OK) {
        ESP_LOGE(TAG, "Помилка встановлення Content-Type сервера");
        return res;
    }

    ESP_LOGI(TAG, "Клієнт підключився до відеопотоку");

    // Цикл трансляції кадрів
    while (true) {
        // Захоплення кадру з камери
        fb = esp_camera_fb_get();
        if (!fb) {
            ESP_LOGE(TAG, "Збій захоплення кадру з сенсора");
            res = ESP_FAIL;
            break;
        }

        if (fb->format != PIXFORMAT_JPEG) {
            // Якщо формат не JPEG, виконується конвертація
            bool jpeg_converted = frame2jpg(fb, 80, &_jpg_buf, &_jpg_buf_len);
            esp_camera_fb_return(fb);
            fb = NULL;
            if (!jpeg_converted) {
                ESP_LOGE(TAG, "Збій стиснення кадру в JPEG");
                res = ESP_FAIL;
                break;
            }
        } else {
            _jpg_buf_len = fb->len;
            _jpg_buf = fb->buf;
        }

        // Передача розділювальної межі між кадрами
        res = httpd_resp_send_chunk(req, _STREAM_BOUNDARY, strlen(_STREAM_BOUNDARY));
        if (res != ESP_OK) {
            if (fb) esp_camera_fb_return(fb);
            else free(_jpg_buf);
            break;
        }

        // Форматування заголовка окремого JPEG-кадру
        size_t hlen = snprintf(part_buf, sizeof(part_buf), _STREAM_PART, (unsigned int)_jpg_buf_len);
        res = httpd_resp_send_chunk(req, part_buf, hlen);
        if (res != ESP_OK) {
            if (fb) esp_camera_fb_return(fb);
            else free(_jpg_buf);
            break;
        }

        // Передача бінарних даних JPEG
        res = httpd_resp_send_chunk(req, (const char *)_jpg_buf, _jpg_buf_len);

        // Обов'язкове вивільнення буфера кадру в драйвер камери
        if (fb) {
            esp_camera_fb_return(fb);
            fb = NULL;
            _jpg_buf = NULL;
        } else if (_jpg_buf) {
            free(_jpg_buf);
            _jpg_buf = NULL;
        }

        if (res != ESP_OK) {
            // Клієнт відключився від потоку
            break;
        }

        // Короткий відпочинок для запобігання перевантаженню процесорного ядра
        vTaskDelay(pdMS_TO_TICKS(10));
    }

    ESP_LOGI(TAG, "Клієнт відключився від відеопотоку");
    return res;
}

esp_err_t start_mjpeg_server(void)
{
    httpd_config_t config = HTTPD_DEFAULT_CONFIG();
    config.server_port = 80;

    httpd_uri_t stream_uri = {
        .uri       = "/stream",
        .method    = HTTP_GET,
        .handler   = stream_handler,
        .user_ctx  = NULL
    };

    ESP_LOGI(TAG, "Запуск HTTP-сервера на порту: %d", config.server_port);
    if (httpd_start(&stream_httpd, &config) == ESP_OK) {
        httpd_register_uri_handler(stream_httpd, &stream_uri);
        return ESP_OK;
    }

    ESP_LOGE(TAG, "Збій старту HTTP-сервера");
    return ESP_FAIL;
}

esp_err_t stop_mjpeg_server(void)
{
    if (stream_httpd) {
        httpd_stop(stream_httpd);
        stream_httpd = NULL;
        ESP_LOGI(TAG, "HTTP-сервер зупинено");
    }
    return ESP_OK;
}
