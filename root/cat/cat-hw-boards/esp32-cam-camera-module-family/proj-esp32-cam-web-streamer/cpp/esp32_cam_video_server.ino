#include <Arduino.h>
#include <WiFi.h>
#include "esp_camera.h"
#include "esp_http_server.h"
#include "FS.h"
#include "SD_MMC.h"
#include "camera_pins.h"

// Параметри бездротової мережі
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// Заголовок специфікації MJPEG потоку
#define PART_BOUNDARY "123456789000000000000987654321"
static const char* _STREAM_CONTENT_TYPE = "multipart/x-mixed-replace; boundary=" PART_BOUNDARY;
static const char* _STREAM_BOUNDARY = "\r\n--" PART_BOUNDARY "\r\n";
static const char* _STREAM_PART = "Content-Type: image/jpeg\r\nContent-Length: %u\r\n\r\n";

httpd_handle_t camera_httpd = NULL;
static uint32_t photo_count = 0;

// Обробник HTTP-запиту потокового відео (MJPEG stream)
static esp_err_t stream_handler(httpd_req_t *req) {
    camera_fb_t *fb = NULL;
    esp_err_t res = ESP_OK;
    size_t _jpg_buf_len = 0;
    uint8_t *_jpg_buf = NULL;
    char part_buf[128];

    res = httpd_resp_set_type(req, _STREAM_CONTENT_TYPE);
    if (res != ESP_OK) {
        return res;
    }

    while (true) {
        fb = esp_camera_fb_get();
        if (!fb) {
            Serial.println("Помилка захоплення кадру з камери");
            res = ESP_FAIL;
        } else {
            if (fb->format != PIXFORMAT_JPEG) {
                bool jpeg_converted = frame2jpg(fb, 80, &_jpg_buf, &_jpg_buf_len);
                esp_camera_fb_return(fb);
                fb = NULL;
                if (!jpeg_converted) {
                    Serial.println("Помилка стиснення кадру в JPEG");
                    res = ESP_FAIL;
                }
            } else {
                _jpg_buf_len = fb->len;
                _jpg_buf = fb->buf;
            }
        }

        if (res == ESP_OK) {
            res = httpd_resp_send_chunk(req, _STREAM_BOUNDARY, strlen(_STREAM_BOUNDARY));
        }
        if (res == ESP_OK) {
            size_t hlen = snprintf(part_buf, sizeof(part_buf), _STREAM_PART, _jpg_buf_len);
            res = httpd_resp_send_chunk(req, part_buf, hlen);
        }
        if (res == ESP_OK) {
            res = httpd_resp_send_chunk(req, (const char *)_jpg_buf, _jpg_buf_len);
        }

        if (fb) {
            esp_camera_fb_return(fb);
            fb = NULL;
            _jpg_buf = NULL;
        } else if (_jpg_buf) {
            free(_jpg_buf);
            _jpg_buf = NULL;
        }

        if (res != ESP_OK) {
            break;
        }
    }

    return res;
}

// Обробник HTTP-запиту збереження знімка на MicroSD карту
static esp_err_t capture_handler(httpd_req_t *req) {
    camera_fb_t *fb = esp_camera_fb_get();
    if (!fb) {
        Serial.println("Не вдалося одержати кадр для знімка");
        httpd_resp_send_500(req);
        return ESP_FAIL;
    }

    photo_count++;
    String path = "/photo_" + String(photo_count) + ".jpg";

    File file = SD_MMC.open(path.c_str(), FILE_WRITE);
    if (!file) {
        Serial.printf("Не вдалося відкрити файл %s для запису\n", path.c_str());
        esp_camera_fb_return(fb);
        httpd_resp_send_500(req);
        return ESP_FAIL;
    }

    file.write(fb->buf, fb->len);
    file.close();
    Serial.printf("Знімок збережено: %s (%u байтів)\n", path.c_str(), fb->len);

    esp_camera_fb_return(fb);

    String response = "Знімок збережено на MicroSD: " + path;
    httpd_resp_sendstr(req, response.c_str());
    return ESP_OK;
}

// Запуск вебсервера з ендпоінтами /stream та /capture
void startCameraServer() {
    httpd_config_t config = HTTPD_DEFAULT_CONFIG();
    config.server_port = 80;

    httpd_uri_t stream_uri = {
        .uri       = "/stream",
        .method    = HTTP_GET,
        .handler   = stream_handler,
        .user_ctx  = NULL
    };

    httpd_uri_t capture_uri = {
        .uri       = "/capture",
        .method    = HTTP_GET,
        .handler   = capture_handler,
        .user_ctx  = NULL
    };

    if (httpd_start(&camera_httpd, &config) == ESP_OK) {
        httpd_register_uri_handler(camera_httpd, &stream_uri);
        httpd_register_uri_handler(camera_httpd, &capture_uri);
        Serial.println("HTTP-вебсервер відеопотоку успішно запущено на порту 80");
    }
}

void setup() {
    Serial.begin(115200);
    Serial.setDebugOutput(true);
    Serial.println("\nЗапуск проєкту автономного відеосервера ESP32-CAM...");

    // Налаштування конфігураційної структури камери
    camera_config_t config;
    config.ledc_channel = LEDC_CHANNEL_0;
    config.ledc_timer = LEDC_TIMER_0;
    config.pin_d0 = Y2_GPIO_NUM;
    config.pin_d1 = Y3_GPIO_NUM;
    config.pin_d2 = Y4_GPIO_NUM;
    config.pin_d3 = Y5_GPIO_NUM;
    config.pin_d4 = Y6_GPIO_NUM;
    config.pin_d5 = Y7_GPIO_NUM;
    config.pin_d6 = Y8_GPIO_NUM;
    config.pin_d7 = Y9_GPIO_NUM;
    config.pin_xclk = XCLK_GPIO_NUM;
    config.pin_pclk = PCLK_GPIO_NUM;
    config.pin_vsync = VSYNC_GPIO_NUM;
    config.pin_href = HREF_GPIO_NUM;
    config.pin_sccb_sda = SIOD_GPIO_NUM;
    config.pin_sccb_scl = SIOC_GPIO_NUM;
    config.pin_pwdn = PWDN_GPIO_NUM;
    config.pin_reset = RESET_GPIO_NUM;
    config.xclk_freq_hz = 20000000;
    config.pixel_format = PIXFORMAT_JPEG;

    // Перевірка наявності зовнішньої пам'яті PSRAM
    if (psramFound()) {
        config.frame_size = FRAMESIZE_VGA;
        config.jpeg_quality = 12;
        config.fb_count = 2;
        config.grab_mode = CAMERA_GRAB_LATEST;
        Serial.println("Виявлено PSRAM: увімкнено подвійний кадровий буфер та роздільність VGA");
    } else {
        config.frame_size = FRAMESIZE_SVGA;
        config.jpeg_quality = 12;
        config.fb_count = 1;
        config.grab_mode = CAMERA_GRAB_WHEN_EMPTY;
        Serial.println("PSRAM не знайдено: обмеження буфера в SRAM");
    }

    // Ініціалізація драйвера камери
    esp_err_t err = esp_camera_init(&config);
    if (err != ESP_OK) {
        Serial.printf("Помилка ініціалізації камери код: 0x%x\n", err);
        return;
    }

    // Оптимізація орієнтації зображення для OV2640
    sensor_t * s = esp_camera_sensor_get();
    if (s != NULL) {
        s->set_vflip(s, 1);
        s->set_hmirror(s, 0);
    }

    // Підключення MicroSD карти у 1-бітовому режимі SD_MMC (другий аргумент true)
    // 1-бітовий режим звільняє GPIO4 від конфлікту з SD-картою
    if (!SD_MMC.begin("/sdcard", true)) {
        Serial.println("Помилка монтування карти пам'яті MicroSD в 1-бітовому режимі SD_MMC");
    } else {
        uint8_t cardType = SD_MMC.cardType();
        if (cardType == CARD_NONE) {
            Serial.println("Карту MicroSD не знайдено в слоті");
        } else {
            Serial.printf("MicroSD успішно змонтовано. Обсяг: %llu МБ\n", SD_MMC.cardSize() / (1024 * 1024));
        }
    }

    // Підключення до мережі Wi-Fi
    WiFi.begin(ssid, password);
    Serial.print("Підключення до Wi-Fi");
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\nWi-Fi підключено!");
    Serial.print("IP-адреса відеосервера: http://");
    Serial.println(WiFi.localIP());

    // Запуск HTTP-сервера
    startCameraServer();
}

void loop() {
    // Всі HTTP-запити обробляються у фонових тасках FreeRTOS вебсервера esp_http_server
    delay(10000);
}
