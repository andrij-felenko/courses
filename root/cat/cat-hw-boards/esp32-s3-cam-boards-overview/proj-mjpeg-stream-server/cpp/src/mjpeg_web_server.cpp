#include "mjpeg_web_server.hpp"
#include <esp_log.h>

static const char* TAG = "MjpegWebServer";

// HTML/JS Веб-інтерфейс керування камерою ESP32-S3
static const char INDEX_HTML[] PROGMEM = R"rawliteral(
<!DOCTYPE html>
<html lang="uk">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ESP32-S3 Відеосервер</title>
    <style>
        body { font-family: Arial, sans-serif; background: #121212; color: #eee; margin: 0; padding: 20px; text-align: center; }
        h1 { color: #4CAF50; }
        .container { max-width: 900px; margin: 0 auto; background: #1e1e1e; padding: 20px; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.5); }
        .video-container { width: 100%; min-height: 360px; background: #000; border-radius: 8px; overflow: hidden; display: flex; align-items: center; justify-content: center; }
        img { max-width: 100%; height: auto; display: block; }
        .controls { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-top: 20px; text-align: left; }
        .control-card { background: #2a2a2a; padding: 15px; border-radius: 8px; }
        label { font-weight: bold; display: block; margin-bottom: 5px; font-size: 14px; }
        select, input[type=range] { width: 100%; padding: 8px; border-radius: 4px; border: none; background: #3a3a3a; color: #fff; }
        .status { margin-top: 15px; font-size: 14px; color: #888; }
    </style>
</head>
<body>
    <div class="container">
        <h1>ESP32-S3 Камера та Відеосервер</h1>
        <div class="video-container">
            <img id="stream" src="/stream" alt="MJPEG Відеопотік">
        </div>
        <div class="controls">
            <div class="control-card">
                <label for="resolution">Роздільна здатність</label>
                <select id="resolution" onchange="sendCommand('set_framesize', parseInt(this.value))">
                    <option value="10">VGA (640x480)</option>
                    <option value="8">SVGA (800x600)</option>
                    <option value="6">QVGA (320x240)</option>
                    <option value="11">HD (1280x720)</option>
                </select>
            </div>
            <div class="control-card">
                <label for="quality">Якість JPEG (1-63)</label>
                <input type="range" id="quality" min="5" max="50" value="12" onchange="sendCommand('set_quality', parseInt(this.value))">
            </div>
            <div class="control-card">
                <label for="brightness">Яскравість (-2..2)</label>
                <input type="range" id="brightness" min="-2" max="2" value="0" onchange="sendCommand('set_brightness', parseInt(this.value))">
            </div>
            <div class="control-card">
                <label for="contrast">Контраст (-2..2)</label>
                <input type="range" id="contrast" min="-2" max="2" value="0" onchange="sendCommand('set_contrast', parseInt(this.value))">
            </div>
        </div>
        <div class="status" id="status-box">Підключення WebSocket...</div>
    </div>

    <script>
        let ws = new WebSocket(`ws://${location.host}/ws`);
        ws.onopen = () => {
            document.getElementById('status-box').innerText = 'WebSocket підключено';
            ws.send(JSON.stringify({action: 'get_status'}));
        };
        ws.onmessage = (event) => {
            let data = JSON.parse(event.data);
            if (data.status === 'ok') {
                document.getElementById('status-box').innerText = 
                    `Вільна PSRAM: ${(data.psram_free / 1024).toFixed(1)} KB | Вільна RAM: ${(data.heap_free / 1024).toFixed(1)} KB | Клієнтів WS: ${data.ws_clients}`;
            }
        };
        ws.onclose = () => { document.getElementById('status-box').innerText = 'WebSocket відключено'; };

        function sendCommand(action, value) {
            if (ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify({action: action, value: value}));
            }
        }
    </script>
</body>
</html>
)rawliteral";

MjpegWebServer::MjpegWebServer(Esp32CameraWrapper& camera, uint16_t port)
    : camera_(camera), port_(port), server_(port), ws_("/ws") {}

MjpegWebServer::~MjpegWebServer() {
    stop();
}

bool MjpegWebServer::begin() {
    if (running_) return true;

    // Налаштування WebSocket обробника
    ws_.onEvent([this](AsyncWebSocket* server, AsyncWebSocketClient* client,
                       AwsEventType type, void* arg, uint8_t* data, size_t len) {
        onWebSocketEvent(server, client, type, arg, data, len);
    });

    server_.addHandler(&ws_);
    setupRoutes();

    server_.begin();
    running_ = true;
    ESP_LOGI(TAG, "Веб-сервер запущено на порту %u", port_);
    return true;
}

void MjpegWebServer::stop() {
    if (!running_) return;
    ws_.closeAll();
    server_.end();
    running_ = false;
    ws_client_count_ = 0;
    ESP_LOGI(TAG, "Веб-сервер зупинено.");
}

void MjpegWebServer::setupRoutes() {
    // Головна сторінка UI
    server_.on("/", HTTP_GET, [this](AsyncWebServerRequest* request) {
        handleRoot(request);
    });

    // MJPEG Відеопотік
    server_.on("/stream", HTTP_GET, [this](AsyncWebServerRequest* request) {
        handleMjpegStream(request);
    });

    // Обробка неіснуючих маршрутів
    server_.onNotFound([](AsyncWebServerRequest* request) {
        request->send(404, "text/plain", "Маршрут не знайдено");
    });
}

void MjpegWebServer::handleRoot(AsyncWebServerRequest* request) {
    request->send_P(200, "text/html", INDEX_HTML);
}

void MjpegWebServer::handleMjpegStream(AsyncWebServerRequest* request) {
    // Режим потокової передачі кадрів через HTTP Chunked Response (multipart/x-mixed-replace)
    AsyncWebServerResponse* response = request->beginChunkedResponse(
        "multipart/x-mixed-replace; boundary=frame",
        [this](uint8_t* buffer, size_t maxLen, size_t index) -> size_t {
            static FrameBufferGuard current_frame;
            static size_t frame_offset = 0;
            static enum { STATE_HEADER, STATE_BODY, STATE_FOOTER } state = STATE_HEADER;
            static char header_buf[128];
            static size_t header_len = 0;

            if (index == 0) {
                state = STATE_HEADER;
                frame_offset = 0;
                current_frame.reset();
            }

            if (state == STATE_HEADER) {
                current_frame = camera_.captureFrame();
                if (!current_frame.valid()) {
                    return 0; // Немає кадру, завершуємо чанк
                }

                header_len = snprintf(header_buf, sizeof(header_buf),
                    "--frame\r\nContent-Type: image/jpeg\r\nContent-Length: %u\r\n\r\n",
                    (unsigned int)current_frame.size());

                size_t to_copy = (header_len < maxLen) ? header_len : maxLen;
                memcpy(buffer, header_buf, to_copy);
                state = STATE_BODY;
                frame_offset = 0;
                return to_copy;
            }

            if (state == STATE_BODY) {
                if (!current_frame.valid()) return 0;

                size_t remaining = current_frame.size() - frame_offset;
                size_t to_copy = (remaining < maxLen) ? remaining : maxLen;
                memcpy(buffer, current_frame.data() + frame_offset, to_copy);
                frame_offset += to_copy;

                if (frame_offset >= current_frame.size()) {
                    state = STATE_FOOTER;
                }
                return to_copy;
            }

            if (state == STATE_FOOTER) {
                static const char footer[] = "\r\n";
                size_t len = sizeof(footer) - 1;
                memcpy(buffer, footer, len);
                state = STATE_HEADER; // Готовність до наступного кадру
                current_frame.reset();
                return len;
            }

            return 0;
        }
    );

    response->addHeader("Access-Control-Allow-Origin", "*");
    response->addHeader("Cache-Control", "no-cache, private, no-store, must-revalidate");
    response->addHeader("Pragma", "no-cache");
    request->send(response);
}

void MjpegWebServer::onWebSocketEvent(AsyncWebSocket* server, AsyncWebSocketClient* client,
                                      AwsEventType type, void* arg, uint8_t* data, size_t len) {
    switch (type) {
        case WS_EVT_CONNECT:
            ws_client_count_++;
            ESP_LOGI(TAG, "WebSocket клієнт #%u підключився з IP: %s (Всього: %u)",
                     client->id(), client->remoteIP().toString().c_str(), ws_client_count_.load());
            sendStatusJson(client);
            break;

        case WS_EVT_DISCONNECT:
            if (ws_client_count_ > 0) ws_client_count_--;
            ESP_LOGI(TAG, "WebSocket клієнт #%u відключився (Всього: %u)", client->id(), ws_client_count_.load());
            break;

        case WS_EVT_DATA: {
            AwsFrameInfo* info = (AwsFrameInfo*)arg;
            if (info->final && info->index == 0 && info->len == len && info->opcode == WS_TEXT) {
                processWebSocketCommand(client, data, len);
            }
            break;
        }

        default:
            break;
    }
}

void MjpegWebServer::processWebSocketCommand(AsyncWebSocketClient* client, uint8_t* data, size_t len) {
    JsonDocument doc;
    DeserializationError err = deserializeJson(doc, data, len);

    if (err) {
        ESP_LOGE(TAG, "Помилка розбору WebSocket JSON: %s", err.c_str());
        return;
    }

    const char* action = doc["action"] | "";
    if (strcmp(action, "set_quality") == 0) {
        int val = doc["value"] | 12;
        camera_.setJpegQuality(val);
    } else if (strcmp(action, "set_framesize") == 0) {
        int val = doc["value"] | 10;
        camera_.setFrameSize((framesize_t)val);
    } else if (strcmp(action, "set_brightness") == 0) {
        int val = doc["value"] | 0;
        camera_.setBrightness(val);
    } else if (strcmp(action, "set_contrast") == 0) {
        int val = doc["value"] | 0;
        camera_.setContrast(val);
    } else if (strcmp(action, "get_status") == 0) {
        sendStatusJson(client);
        return;
    }

    // Надсилаємо оновлений статус усім активним клієнтам
    JsonDocument statusDoc;
    statusDoc["status"] = "ok";
    statusDoc["psram_free"] = ESP.getFreePsram();
    statusDoc["heap_free"] = ESP.getFreeHeap();
    statusDoc["ws_clients"] = ws_client_count_.load();

    String responseStr;
    serializeJson(statusDoc, responseStr);
    ws_.textAll(responseStr);
}

void MjpegWebServer::sendStatusJson(AsyncWebSocketClient* client) {
    if (!client) return;

    JsonDocument doc;
    doc["status"] = "ok";
    doc["psram_free"] = ESP.getFreePsram();
    doc["heap_free"] = ESP.getFreeHeap();
    doc["ws_clients"] = ws_client_count_.load();

    String responseStr;
    serializeJson(doc, responseStr);
    client->text(responseStr);
}

void MjpegWebServer::update() {
    if (!running_ || ws_client_count_.load() == 0) return;

    uint32_t now = millis();
    if (now - last_frame_time_ms_ >= frame_interval_ms_) {
        last_frame_time_ms_ = now;

        // Трансляція бінарного JPEG кадру по WebSocket для підключених клієнтів
        auto guard = camera_.captureFrame();
        if (guard.valid()) {
            ws_.binaryAll(guard.data(), guard.size());
        }
    }
}
