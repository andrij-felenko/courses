#include <Arduino.h>
#include <WiFi.h>
#include "esp_camera.h"
#include "esp_http_server.h"
#include "camera_pins.h"

// Параметри підключення до бездротової мережі Wi-Fi
constexpr const char* WIFI_SSID     = "Your_WiFi_SSID";
constexpr const char* WIFI_PASSWORD = "Your_WiFi_Password";

// Граничний маркер для розділення кадрів у MJPEG-відеопотоці (HTTP Multipart boundary)
#define PART_BOUNDARY "123456789000000000000987654321"
static const char* STREAM_CONTENT_TYPE = "multipart/x-mixed-replace; boundary=" PART_BOUNDARY;

// Дескриптор фонового HTTP-сервера
static httpd_handle_t stream_httpd = nullptr;

/**
 * Налаштування конфігурації та ініціалізація сенсора камери OV2640 з перевіркою PSRAM.
 * @return true у разі успішної ініціалізації, false при виникненні помилки.
 */
bool init_camera() {
    camera_config_t config{};
    config.ledc_channel = LEDC_CHANNEL_0;
    config.ledc_timer   = LEDC_TIMER_0;
    config.pin_d0       = Y2_GPIO_NUM;
    config.pin_d1       = Y3_GPIO_NUM;
    config.pin_d2       = Y4_GPIO_NUM;
    config.pin_d3       = Y5_GPIO_NUM;
    config.pin_d4       = Y6_GPIO_NUM;
    config.pin_d5       = Y7_GPIO_NUM;
    config.pin_d6       = Y8_GPIO_NUM;
    config.pin_d7       = Y9_GPIO_NUM;
    config.pin_xclk     = XCLK_GPIO_NUM;
    config.pin_pclk     = PCLK_GPIO_NUM;
    config.pin_vsync    = VSYNC_GPIO_NUM;
    config.pin_href     = HREF_GPIO_NUM;
    config.pin_sccb_sda = SIOD_GPIO_NUM;
    config.pin_sccb_scl = SIOC_GPIO_NUM;
    config.pin_pwdn     = PWDN_GPIO_NUM;
    config.pin_reset    = RESET_GPIO_NUM;
    config.xclk_freq_hz = 20000000;
    config.pixel_format = PIXFORMAT_JPEG;

    // Автоматичний вибір режимів буферизації залежно від наявності зовнішньої PSRAM
    if (psramFound()) {
        config.frame_size   = FRAMESIZE_UXGA; // 1600x1200
        config.jpeg_quality = 10;             // Висока якість (шкала 10-63)
        config.fb_count     = 2;              // Подвійна буферизація в PSRAM
        config.grab_mode    = CAMERA_GRAB_LATEST;
    } else {
        config.frame_size   = FRAMESIZE_SVGA; // 800x600 без PSRAM
        config.jpeg_quality = 12;
        config.fb_count     = 1;
        config.fb_location = CAMERA_FB_IN_DRAM;
    }

    // Запуск драйвера камери
    esp_err_t err = esp_camera_init(&config);
    if (err != ESP_OK) {
        Serial.printf("Помилка ініціалізації драйвера камери: 0x%x\n", err);
        return false;
    }

    // Тонке налаштування сенсора OV2640
    sensor_t* sensor = esp_camera_sensor_get();
    if (sensor != nullptr && sensor->id.PID == OV2640_PID) {
        sensor->set_vflip(sensor, 1);      // Вертикальна орієнтація кадру
        sensor->set_hmirror(sensor, 0);    // Дзеркальне відображення
        sensor->set_brightness(sensor, 1); // Корекція яскравості (-2..2)
        sensor->set_saturation(sensor, 0); // Корекція насиченості (-2..2)
    }

    Serial.println("Сенсор камери OV2640 успішно налаштовано.");
    return true;
}

/**
 * Обробник головної сторінки з HTML-інтерфейсом для перегляду трансляції.
 */
esp_err_t index_handler(httpd_req_t* req) {
    static const char* index_html = R"rawliteral(
<!DOCTYPE html>
<html lang="uk">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ESP32-CAM MJPEG Stream</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #1e1e2e;
            color: #cdd6f4;
            text-align: center;
            margin: 0;
            padding: 20px;
        }
        h1 { color: #89b4fa; }
        .card {
            display: inline-block;
            background-color: #313244;
            padding: 15px;
            border-radius: 12px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
        }
        img {
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            display: block;
        }
    </style>
</head>
<body>
    <h1>ESP32-CAM MJPEG Відеотрансляція</h1>
    <div class="card">
        <img src="/stream" alt="Відеопотік з камери">
    </div>
</body>
</html>
)rawliteral";

    httpd_resp_set_type(req, "text/html; charset=utf-8");
    return httpd_resp_send(req, index_html, HTTPD_RESP_USE_STRLEN);
}

/**
 * Обробник HTTP-ендпоінта /stream для неперервної передачі MJPEG-потоку.
 */
esp_err_t stream_handler(httpd_req_t* req) {
    camera_fb_t* fb = nullptr;
    esp_err_t res = ESP_OK;
    char part_buf[128];

    // Встановлення відповідного HTTP-заголовка для multipart передачі кадрів
    httpd_resp_set_type(req, STREAM_CONTENT_TYPE);
    httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");

    while (true) {
        // Отримання чергового кадру з розширеної пам'яті PSRAM/DRAM
        fb = esp_camera_fb_get();
        if (!fb) {
            Serial.println("Помилка при зчитуванні кадру з камери.");
            res = ESP_FAIL;
            break;
        }

        // Формування метаданих кадру JPEG для браузера
        size_t hlen = snprintf(part_buf, sizeof(part_buf),
            "--" PART_BOUNDARY "\r\nContent-Type: image/jpeg\r\nContent-Length: %u\r\n\r\n",
            static_cast<unsigned int>(fb->len));

        // Відправка заголовка кадру
        res = httpd_resp_send_chunk(req, part_buf, hlen);
        if (res == ESP_OK) {
            // Відправка безпосередньо бінарних даних кадру JPEG
            res = httpd_resp_send_chunk(req, reinterpret_cast<const char*>(fb->buf), fb->len);
        }
        if (res == ESP_OK) {
            // Відправка розділювача між кадрами
            res = httpd_resp_send_chunk(req, "\r\n", 2);
        }

        // Звільнення буфера кадру обов'язкове для звільнення пам'яті під наступні кадри
        esp_camera_fb_return(fb);
        fb = nullptr;

        if (res != ESP_OK) {
            // Вихід з циклу трансляції в разі розриву з'єднання клієнтом
            break;
        }
    }

    return res;
}

/**
 * Запуск HTTP-сервера та реєстрація URL-маршрутів.
 */
bool start_camera_server() {
    httpd_config_t config = HTTPD_DEFAULT_CONFIG();
    config.server_port = 80;

    httpd_uri_t index_uri = {
        .uri      = "/",
        .method   = HTTP_GET,
        .handler  = index_handler,
        .user_ctx = nullptr
    };

    httpd_uri_t stream_uri = {
        .uri      = "/stream",
        .method   = HTTP_GET,
        .handler  = stream_handler,
        .user_ctx = nullptr
    };

    if (httpd_start(&stream_httpd, &config) == ESP_OK) {
        httpd_register_uri_handler(stream_httpd, &index_uri);
        httpd_register_uri_handler(stream_httpd, &stream_uri);
        Serial.printf("HTTP-вебсервер успішно запущено на порту %d.\n", config.server_port);
        return true;
    }

    Serial.println("Помилка запуску HTTP-сервера.");
    return false;
}

void setup() {
    // Налаштування послідовного порту для обміну даними через прошивач CH340
    Serial.begin(115200);
    Serial.setDebugOutput(true);
    Serial.println();
    Serial.println("=== Запуск системи ESP32-CAM ===");

    // 1. Ініціалізація сенсора камери OV2640
    if (!init_camera()) {
        Serial.println("Критичний збій: не вдалося налаштувати камеру!");
        return;
    }

    // 2. З'єднання з локальною мережею Wi-Fi
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    Serial.print("З'єднання з Wi-Fi ");
    Serial.print(WIFI_SSID);

    int retries = 0;
    while (WiFi.status() != WL_CONNECTED && retries < 30) {
        delay(500);
        Serial.print(".");
        retries++;
    }
    Serial.println();

    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("Помилка підключення до Wi-Fi! Перевірте облікові дані.");
        return;
    }

    Serial.print("Успішне підключення. Присвоєна IP-адреса: ");
    Serial.println(WiFi.localIP());

    // 3. Запуск вебсервера та публікація відеопотоку
    if (start_camera_server()) {
        Serial.println("Трансляція запущена:");
        Serial.printf("  Веб-інтерфейс: http://%s/\n", WiFi.localIP().toString().c_str());
        Serial.printf("  MJPEG-потік:   http://%s/stream\n", WiFi.localIP().toString().c_str());
    }
}

void loop() {
    // Головний цикл вільний, оскільки обробка HTTP-запитів виконується асинхронно сервером
    delay(10000);
}
