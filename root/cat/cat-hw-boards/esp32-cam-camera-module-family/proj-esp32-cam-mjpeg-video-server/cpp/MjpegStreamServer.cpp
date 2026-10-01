#include "MjpegStreamServer.hpp"
#include "CameraConfig.hpp"
#include <esp_log.h>
#include <Arduino.h>

static const char* TAG = "MJPEG_SERVER";

constexpr std::string_view STREAM_BOUNDARY = "123456789000000000000987654321";

MjpegStreamServer::~MjpegStreamServer() {
    stop();
}

bool MjpegStreamServer::begin(uint16_t port) {
    if (isRunning_) {
        return true;
    }

    // Крок 1. Ініціалізація камери OV2640
    camera_config_t config = get_ai_thinker_camera_config();
    esp_err_t err = esp_camera_init(&config);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Помилка ініціалізації камери: 0x%x", err);
        return false;
    }

    // Крок 2. Конфігурування та запуск HTTP-сервера
    httpd_config_t httpdConfig = HTTPD_DEFAULT_CONFIG();
    httpdConfig.server_port = port;
    httpdConfig.ctrl_port = port + 1;

    err = httpd_start(&serverHandle_, &httpdConfig);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Не вдалося запустити HTTP-сервер: 0x%x", err);
        return false;
    }

    // Крок 3. Реєстрація URI-маршруту /stream
    httpd_uri_t streamUri = {
        .uri      = "/stream",
        .method   = HTTP_GET,
        .handler  = MjpegStreamServer::streamHandler,
        .user_ctx = nullptr
    };

    httpd_register_uri_handler(serverHandle_, &streamUri);
    isRunning_ = true;
    ESP_LOGI(TAG, "MJPEG Відеосервер успішно запущено на порту %d", port);
    return true;
}

void MjpegStreamServer::stop() {
    if (serverHandle_) {
        httpd_stop(serverHandle_);
        serverHandle_ = nullptr;
    }
    isRunning_ = false;
}

esp_err_t MjpegStreamServer::streamHandler(httpd_req_t* req) {
    esp_err_t res = ESP_OK;
    char partHeader[128];

    // Встановлення типу вмісту відповіді multipart/x-mixed-replace
    res = httpd_resp_set_type(req, "multipart/x-mixed-replace; boundary=123456789000000000000987654321");
    if (res != ESP_OK) {
        return res;
    }

    httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");

    // Безперервний цикл трансляції MJPEG-кадрів
    while (true) {
        // Отримання фреймбуфера з автозвільненням через RAII
        FrameBuffer fb(esp_camera_fb_get());
        if (!fb.valid()) {
            ESP_LOGE(TAG, "Помилка захоплення кадру з камери");
            res = ESP_FAIL;
            break;
        }

        // Формування HTTP-заголовка кадру
        size_t hlen = snprintf(partHeader, sizeof(partHeader),
                               "\r\n--123456789000000000000987654321\r\n"
                               "Content-Type: image/jpeg\r\n"
                               "Content-Length: %u\r\n\r\n",
                               (unsigned int)fb.get()->len);

        res = httpd_resp_send_chunk(req, partHeader, hlen);
        if (res != ESP_OK) {
            break;
        }

        // Відправка бінарного бітрейту JPEG-кадру
        res = httpd_resp_send_chunk(req, (const char*)fb.get()->buf, fb.get()->len);
        if (res != ESP_OK) {
            break;
        }
    }

    return res;
}
