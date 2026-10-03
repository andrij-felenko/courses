#ifndef MJPEG_ASYNC_SERVER_HPP
#define MJPEG_ASYNC_SERVER_HPP

#include <esp_http_server.h>
#include <Arduino.h>
#include <cstdint>
#include <cstdio>
#include "PsramFrameBuffer.hpp"
#include "FlashPwmController.hpp"

/**
 * @brief Клас асинхронного Wi-Fi вебсервера для трансляції MJPEG-відеопотоку.
 * 
 * Обробляє HTTP-запити у фоновій задачі FreeRTOS, транслює кадрові буфери з PSRAM
 * клієнтам без блокування основного циклу виконання прошивки.
 */
class MjpegAsyncServer {
public:
    static constexpr const char* STREAM_CONTENT_TYPE = "multipart/x-mixed-replace; boundary=frame";
    static constexpr const char* STREAM_BOUNDARY = "\r\n--frame\r\nContent-Type: image/jpeg\r\nContent-Length: ";

    MjpegAsyncServer(PsramFrameBuffer& cameraBuffer, FlashPwmController& flashController)
        : cameraBuffer_(cameraBuffer), flashController_(flashController) {}

    ~MjpegAsyncServer() {
        stop();
    }

    MjpegAsyncServer(const MjpegAsyncServer&) = delete;
    MjpegAsyncServer& operator=(const MjpegAsyncServer&) = delete;

    /**
     * @brief Запускає HTTP-сервер на вказаному порту та реєструє URI-маршрути.
     * @param port Номер мережевого порту (за замовчуванням 80).
     * @return true у разі успішного запуску, false при помилці.
     */
    bool start(uint16_t port = 80) {
        if (serverHandle_ != nullptr) {
            return true; // Сервер вже запущено
        }

        httpd_config_t config = HTTPD_DEFAULT_CONFIG();
        config.server_port = port;
        config.ctrl_port = port + 1;
        config.max_uri_handlers = 8;
        config.task_priority = tskIDLE_PRIORITY + 5;
        config.stack_size = 8192;

        if (httpd_start(&serverHandle_, &config) != ESP_OK) {
            serverHandle_ = nullptr;
            return false;
        }

        // Реєстрація URI маршруту головної сторінки HTML
        httpd_uri_t indexUri = {
            .uri      = "/",
            .method   = HTTP_GET,
            .handler  = [](httpd_req_t* req) -> esp_err_t {
                auto* self = static_cast<MjpegAsyncServer*>(req->user_ctx);
                return self->handleIndexRequest(req);
            },
            .user_ctx = this
        };
        httpd_register_uri_handler(serverHandle_, &indexUri);

        // Реєстрація URI маршруту відеопотоку MJPEG
        httpd_uri_t streamUri = {
            .uri      = "/stream",
            .method   = HTTP_GET,
            .handler  = [](httpd_req_t* req) -> esp_err_t {
                auto* self = static_cast<MjpegAsyncServer*>(req->user_ctx);
                return self->handleStreamRequest(req);
            },
            .user_ctx = this
        };
        httpd_register_uri_handler(serverHandle_, &streamUri);

        // Реєстрація URI маршруту керування підсвічуванням
        httpd_uri_t ledUri = {
            .uri      = "/led",
            .method   = HTTP_GET,
            .handler  = [](httpd_req_t* req) -> esp_err_t {
                auto* self = static_cast<MjpegAsyncServer*>(req->user_ctx);
                return self->handleLedRequest(req);
            },
            .user_ctx = this
        };
        httpd_register_uri_handler(serverHandle_, &ledUri);

        isRunning_ = true;
        return true;
    }

    /**
     * @brief Зупиняє HTTP-сервер і вивільняє ресурси.
     */
    void stop() {
        if (serverHandle_ != nullptr) {
            httpd_stop(serverHandle_);
            serverHandle_ = nullptr;
            isRunning_ = false;
        }
    }

    /**
     * @brief Перевіряє, чи активний вебсервер.
     */
    bool isRunning() const {
        return isRunning_;
    }

private:
    /**
     * @brief Обробник запиту головної вебсторінки.
     */
    esp_err_t handleIndexRequest(httpd_req_t* req) {
        static const char indexHtml[] = R"rawliteral(
<!DOCTYPE html>
<html lang="uk">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ESP32-CAM Відеострімер</title>
    <style>
        body { font-family: Arial, sans-serif; background: #1a1a1a; color: #fff; text-align: center; margin: 0; padding: 20px; }
        h1 { color: #00adb5; }
        .container { max-width: 800px; margin: 0 auto; background: #222831; padding: 20px; border-radius: 10px; }
        img { width: 100%; max-width: 640px; height: auto; border: 2px solid #00adb5; border-radius: 5px; }
        .controls { margin-top: 20px; display: flex; flex-direction: column; align-items: center; gap: 10px; }
        input[type=range] { width: 80%; max-width: 400px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>ESP32-CAM MJPEG Streamer</h1>
        <img src="/stream" alt="Відеопоток">
        <div class="controls">
            <label for="flash">Підсвічування спалаху (LEDC PWM): <span id="val">0</span>%</label>
            <input type="range" id="flash" min="0" max="100" value="0" oninput="updateFlash(this.value)">
        </div>
    </div>
    <script>
        function updateFlash(val) {
            document.getElementById('val').innerText = val;
            fetch('/led?val=' + val);
        }
    </script>
</body>
</html>
)rawliteral";

        httpd_resp_set_type(req, "text/html");
        return httpd_resp_send(req, indexHtml, strlen(indexHtml));
    }

    /**
     * @brief Обробник безблокувального трансляційного MJPEG-запиту.
     */
    esp_err_t handleStreamRequest(httpd_req_t* req) {
        esp_err_t res = ESP_OK;
        char partHeader[128];

        res = httpd_resp_set_type(req, STREAM_CONTENT_TYPE);
        if (res != ESP_OK) {
            return res;
        }

        httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");

        while (true) {
            // Отримуємо кадр із буфера PSRAM через RAII-обгортку
            Frame frame = cameraBuffer_.acquireFrame();
            if (!frame.isValid()) {
                vTaskDelay(pdMS_TO_TICKS(10));
                continue;
            }

            int hlen = snprintf(partHeader, sizeof(partHeader), 
                                "%s%u\r\n\r\n", STREAM_BOUNDARY, (unsigned int)frame.size());

            // 1. Надсилаємо заголовок кадра
            res = httpd_resp_send_chunk(req, partHeader, hlen);
            if (res != ESP_OK) break;

            // 2. Надсилаємо JPEG дані з PSRAM
            res = httpd_resp_send_chunk(req, reinterpret_cast<const char*>(frame.data()), frame.size());
            if (res != ESP_OK) break;

            // Кадр автоматично повернуто у драйвер після виходу з області видимості об'єкта frame

            // Пауза між кадрами для стабільності вебсервера та FreeRTOS
            vTaskDelay(pdMS_TO_TICKS(30));
        }

        return res;
    }

    /**
     * @brief Обробник HTTP-запиту для налаштування ШІМ-підсвічування спалаху.
     */
    esp_err_t handleLedRequest(httpd_req_t* req) {
        char query[64] = {0};
        if (httpd_req_get_url_query_str(req, query, sizeof(query)) == ESP_OK) {
            char paramVal[16] = {0};
            if (httpd_query_key_value(query, "val", paramVal, sizeof(paramVal)) == ESP_OK) {
                int brightnessPercent = atoi(paramVal);
                flashController_.setBrightnessPercent(static_cast<uint8_t>(brightnessPercent));
            }
        }
        httpd_resp_set_type(req, "text/plain");
        return httpd_resp_sendstr(req, "OK");
    }

    PsramFrameBuffer& cameraBuffer_;
    FlashPwmController& flashController_;
    httpd_handle_t serverHandle_{nullptr};
    bool isRunning_{false};
};

#endif // MJPEG_ASYNC_SERVER_HPP
