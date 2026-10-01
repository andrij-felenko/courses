#include <Arduino.h>
#include <WiFi.h>
#include "CameraPinsOV3640.hpp"
#include "TimelapseStorage.hpp"
#include "VideoStreamer.hpp"

// Налаштування бездротової мережі Wi-Fi
const char* WIFI_SSID = "Your_WiFi_SSID";
const char* WIFI_PASS = "Your_WiFi_Password";

// Об'єкти служб таймлапсу та відеостримінгу
TimelapseStorage timelapse;
VideoStreamer    streamer;

void setup() {
    Serial.begin(115200);
    Serial.println("\n=== Запуск системи ESP32-CAM (OV3640) ===");

    // 1. Ініціалізація апаратної конфігурації камери
    camera_config_t config = createOV3640Config();
    esp_err_t err = esp_camera_init(&config);
    if (err != ESP_OK) {
        Serial.printf("Помилка ініціалізації камери: 0x%x\n", err);
        return;
    }
    Serial.println("[OK] Сенсор OV3640 успішно ініціалізовано.");

    // 2. Ініціалізація карти пам'яті SD_MMC для таймлапс-зйомки
    if (timelapse.begin()) {
        Serial.println("[OK] Файлова система SD_MMC змонтована.");
    } else {
        Serial.println("[ПОПЕРЕДЖЕННЯ] Карта microSD не виявлена. Збереження таймлапсу вимкнено.");
    }

    // 3. Підключення до мережі Wi-Fi
    WiFi.begin(WIFI_SSID, WIFI_PASS);
    Serial.print("Підключення до Wi-Fi");
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\n[OK] Wi-Fi підключено!");
    Serial.print("Адреса відеостриму: http://");
    Serial.print(WiFi.localIP());
    Serial.println("/stream");

    // 4. Запуск HTTP веб-сервера відеопотоку
    if (streamer.start(80)) {
        Serial.println("[OK] MJPEG відеосервер запущено на порту 80.");
    } else {
        Serial.println("[ПОМИЛКА] Не вдалося запустити веб-сервер.");
    }
}

void loop() {
    // Автоматичне збереження кадрів таймлапсу кожні 10 000 мс (10 секунд)
    if (timelapse.isInitialized()) {
        timelapse.process(10000);
    }

    delay(10); // Неблокуюча коротка пауза для фонових задач FreeRTOS
}
