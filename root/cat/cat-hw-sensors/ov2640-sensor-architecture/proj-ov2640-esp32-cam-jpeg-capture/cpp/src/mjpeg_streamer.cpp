#include "mjpeg_streamer.hpp"
#include <esp_log.h>
#include <cstdio>

static const char* TAG = "MJPEG_STREAMER";

// Унікальна межа (boundary) для виокремлення окремих JPEG-кадрів у потоці multipart
#define STREAM_BOUNDARY "123456789000000000000987654321"

static const char* STREAM_CONTENT_TYPE =
    "multipart/x-mixed-replace;boundary=" STREAM_BOUNDARY;

MjpegStreamer::~MjpegStreamer() {
    if (server_ != nullptr) {
        stop();
    }
}

esp_err_t MjpegStreamer::start(uint16_t port, Ov2640Camera& camera) {
    if (server_ != nullptr) {
        ESP_LOGW(TAG, "MJPEG Сервер вже запущено.");
        return ESP_OK;
    }

    if (!camera.isInitialized()) {
        ESP_LOGE(TAG, "Неможливо запустити стример: камера не ініціалізована!");
        return ESP_ERR_INVALID_STATE;
    }

    camera_ = &camera;

    httpd_config_t config = HTTPD_DEFAULT_CONFIG();
    config.server_port = port;
    config.ctrl_port = port + 1;
    config.max_open_sockets = 4;
    config.lru_purge_enable = true;

    esp_err_t err = httpd_start(&server_, &config);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Помилка запуску HTTP-сервера: 0x%x", err);
        return err;
    }

    // Реєстрація URI-маршруту для трансляції відео
    httpd_uri_t stream_uri = {
        .uri      = "/stream",
        .method   = HTTP_GET,
        .handler  = streamHandler,
        .user_ctx = this
    };

    err = httpd_register_uri_handler(server_, &stream_uri);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Помилка реєстрації маршруту /stream: 0x%x", err);
        httpd_stop(server_);
        server_ = nullptr;
        return err;
    }

    ESP_LOGI(TAG, "MJPEG відеосервер успішно запущено на порту %d. URI: /stream", port);
    return ESP_OK;
}

esp_err_t MjpegStreamer::stop() {
    if (server_ == nullptr) {
        return ESP_OK;
    }

    esp_err_t err = httpd_stop(server_);
    if (err == ESP_OK) {
        server_ = nullptr;
        camera_ = nullptr;
        ESP_LOGI(TAG, "MJPEG відеосервер зупинено.");
    } else {
        ESP_LOGE(TAG, "Помилка зупинки HTTP-сервера: 0x%x", err);
    }
    return err;
}

esp_err_t MjpegStreamer::streamHandler(httpd_req_t* req) {
    auto* instance = static_cast<MjpegStreamer*>(req->user_ctx);
    if (instance == nullptr || instance->camera_ == nullptr) {
        httpd_resp_send_500(req);
        return ESP_FAIL;
    }

    esp_err_t res = ESP_OK;
    char part_buf[128];

    // Встановлення відповідного HTTP Content-Type для multipart-потоку
    res = httpd_resp_set_type(req, STREAM_CONTENT_TYPE);
    if (res != ESP_OK) {
        return res;
    }

    // Відключаємо кешування браузером
    httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
    httpd_resp_set_hdr(req, "Cache-Control", "no-cache, private, max-age=0, must-revalidate");

    ESP_LOGI(TAG, "Новий веб-клієнт підключився до MJPEG-потоку.");

    // Безперервний цикл передачі JPEG-кадрів
    while (true) {
        // Отримання кадру через RAII FrameBufferGuard з PSRAM
        FrameBufferGuard fbGuard = instance->camera_->captureFrame();
        if (!fbGuard.isValid()) {
            ESP_LOGE(TAG, "Помилка захоплення кадру під час трансляції.");
            res = ESP_FAIL;
            break;
        }

        // Формування MIME-заголовка для чергового кадру
        int hlen = snprintf(part_buf, sizeof(part_buf),
                            "\r\n--" STREAM_BOUNDARY "\r\nContent-Type: image/jpeg\r\nContent-Length: %u\r\n\r\n",
                            static_cast<unsigned int>(fbGuard.size()));

        // 1. Відправка MIME-заголовка кадру
        res = httpd_resp_send_chunk(req, part_buf, hlen);
        if (res != ESP_OK) {
            break;
        }

        // 2. Відправка бінарних даних JPEG-зображення з PSRAM
        res = httpd_resp_send_chunk(req, reinterpret_cast<const char*>(fbGuard.data()), fbGuard.size());
        if (res != ESP_OK) {
            break;
        }

        // Автоматичне повернення буфера в кадровий драйвер відбувається при виході fbGuard з циклу (деструктор)
    }

    ESP_LOGI(TAG, "Клієнт відключився від MJPEG-потоку.");
    return res;
}
