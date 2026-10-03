// C++: Обробник трансляції відеопотоку у середовищі Arduino для ESP32
#include <Arduino.h>
#include "esp_http_server.h"
#include "esp_camera.h"

class VideoStreamServer {
private:
    httpd_handle_t stream_httpd = NULL;

    static esp_err_t streamHandler(httpd_req_t *req) {
        camera_fb_t *fb = NULL;
        esp_err_t res = ESP_OK;
        char part_buf[128];

        const char* boundary = "\r\n--123456789000000000000987654321\r\n";
        res = httpd_resp_set_type(req, "multipart/x-mixed-replace; boundary=123456789000000000000987654321");
        if (res != ESP_OK) {
            return res;
        }

        while (true) {
            fb = esp_camera_fb_get();
            if (!fb) {
                Serial.println("Не вдалося отримати кадр камери");
                res = ESP_FAIL;
                break;
            }

            res = httpd_resp_send_chunk(req, boundary, strlen(boundary));
            if (res == ESP_OK) {
                size_t hlen = snprintf(part_buf, sizeof(part_buf), 
                                       "Content-Type: image/jpeg\r\nContent-Length: %u\r\n\r\n", 
                                       fb->len);
                res = httpd_resp_send_chunk(req, part_buf, hlen);
            }
            if (res == ESP_OK) {
                res = httpd_resp_send_chunk(req, (const char *)fb->buf, fb->len);
            }

            // Вивільнення буфера кадру назад до драйвера
            esp_camera_fb_return(fb);
            fb = NULL;

            if (res != ESP_OK) {
                // Обробка обриву мережевого з'єднання з боку клієнта
                break;
            }
        }

        return res;
    }

public:
    bool begin(uint61_t port = 80) {
        httpd_config_t config = HTTPD_DEFAULT_CONFIG();
        config.server_port = port;

        httpd_uri_t stream_uri = {
            .uri       = "/stream",
            .method    = HTTP_GET,
            .handler   = streamHandler,
            .user_ctx  = NULL
        };

        if (httpd_start(&stream_httpd, &config) == ESP_OK) {
            httpd_register_uri_handler(stream_httpd, &stream_uri);
            return true;
        }
        return false;
    }
};

VideoStreamServer streamServer;

void setup() {
    Serial.begin(115200);
    // Ініціалізація Wi-Fi та драйвера камери передує запуску сервера
    streamServer.begin(80);
}

void loop() {
    vTaskDelay(pdMS_TO_TICKS(1000));
}
