#include "mjpeg_stream_server.hpp"
#include <WiFi.h>

MjpegStreamServer::MjpegStreamServer(EspCamera& camera, uint16_t port)
    : camera_(camera), server_(port), is_running_(false) {
}

MjpegStreamServer::~MjpegStreamServer() {
    stop();
}

void MjpegStreamServer::begin() {
    if (is_running_) return;

    // Реєстрація HTTP-маршрутів
    server_.on("/", [this]() { handleRoot(); });
    server_.on("/stream", [this]() { handleStream(); });
    server_.onNotFound([this]() { handleNotFound(); });

    server_.begin();
    is_running_ = true;
    Serial.println(F("[MjpegStreamServer] HTTP WebServer успішно запущено. Ендпоінт: /stream"));
}

void MjpegStreamServer::stop() {
    if (is_running_) {
        server_.stop();
        is_running_ = false;
        Serial.println(F("[MjpegStreamServer] HTTP WebServer зупинено."));
    }
}

void MjpegStreamServer::handleClient() {
    if (is_running_) {
        server_.handleClient();
    }
}

void MjpegStreamServer::handleRoot() {
    String html = F("<!DOCTYPE html><html>"
                    "<head><title>ESP32-CAM MJPEG Stream</title>"
                    "<meta name='viewport' content='width=device-width, initial-scale=1'>"
                    "<style>"
                    "body { font-family: Arial, sans-serif; background: #121212; color: #fff; text-align: center; margin: 0; padding: 20px; }"
                    "h1 { color: #4CAF50; }"
                    "img { max-width: 100%; height: auto; border: 3px solid #333; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.5); }"
                    "</style></head>"
                    "<body>"
                    "<h1>Відеопотік OV2640 (MJPEG)</h1>"
                    "<div><img src='/stream' alt='Live Video Stream'></div>"
                    "</body></html>");
    server_.send(200, "text/html", html);
}

void MjpegStreamServer::handleStream() {
    WiFiClient client = server_.client();

    if (!camera_.isInitialized()) {
        server_.send(500, "text/plain", "Камеру не ініціалізовано!");
        return;
    }

    // Формування HTTP-заголовка для MJPEG-потоку (multipart/x-mixed-replace)
    String response = "HTTP/1.1 200 OK\r\n"
                      "Access-Control-Allow-Origin: *\r\n"
                      "Content-Type: multipart/x-mixed-replace; boundary=" + boundary_ + "\r\n"
                      "Cache-Control: no-cache, private, max-age=0\r\n"
                      "Pragma: no-cache\r\n"
                      "Connection: close\r\n\r\n";

    client.print(response);

    Serial.println(F("[MjpegStreamServer] Розпочато потокову трансляцію MJPEG для клієнта."));

    uint32_t frame_count = 0;
    uint32_t last_log_time = millis();

    while (client.connected()) {
        // RAII-захоплення кадру: об'єкт fb вивільнить пам'ять драйвера наприкінці кожної ітерації циклу
        FrameBufferGuard fb = camera_.captureFrame();

        if (!fb.isValid()) {
            delay(10);
            continue;
        }

        // Заголовок окремого JPEG-кадру в multipart-потоці
        String partHeader = "--" + boundary_ + "\r\n"
                            "Content-Type: image/jpeg\r\n"
                            "Content-Length: " + String(fb.getSize()) + "\r\n\r\n";

        // Відправка заголовка кадру
        if (client.write((const uint8_t*)partHeader.c_str(), partHeader.length()) != partHeader.length()) {
            break; // Клієнт від'єднався
        }

        // Відправка JPEG-бінарних даних із PSRAM
        if (client.write(fb.getBuffer(), fb.getSize()) != fb.getSize()) {
            break; // Клієнт від'єднався
        }

        // Заключний розділювач CRLF
        if (client.write("\r\n", 2) != 2) {
            break;
        }

        frame_count++;
        if (millis() - last_log_time >= 5000) {
            float fps = (float)frame_count / 5.0f;
            Serial.printf("[MjpegStreamServer] Потокова трансляція активна: ~%.1f FPS\n", fps);
            frame_count = 0;
            last_log_time = millis();
        }

        // Мінімальна пауза для віддачі процесорного часу системним задачам Wi-Fi та Watchdog
        delay(1);
    }

    Serial.println(F("[MjpegStreamServer] Клієнт від'єднався. Потік завершено."));
}

void MjpegStreamServer::handleNotFound() {
    server_.send(404, "text/plain", "404: Сторінку не знайдено");
}
