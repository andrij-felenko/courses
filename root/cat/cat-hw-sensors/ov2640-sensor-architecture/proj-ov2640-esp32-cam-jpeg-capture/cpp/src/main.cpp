#include <Arduino.h>
#include <WiFi.h>
#include "ov2640_camera.hpp"
#include "mjpeg_streamer.hpp"

// Конфігурація Wi-Fi мережі (замініть на власні облікові дані)
const char* WIFI_SSID     = "Your_WiFi_SSID";
const char* WIFI_PASSWORD = "Your_WiFi_Password";

// Глобальні екземпляри камери та відеосервера
Ov2640Camera camera;
MjpegStreamer streamer;

void connectToWiFi() {
    Serial.print("Підключення до Wi-Fi мережі: ");
    Serial.println(WIFI_SSID);

    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }

    Serial.println();
    Serial.println("Wi-Fi підключено успішно!");
    Serial.print("IP-адреса ESP32-CAM: http://");
    Serial.println(WiFi.localIP());
}

void setup() {
    Serial.begin(115200);
    delay(1000);

    Serial.println("=== Ініціалізація системи ESP32-CAM (OV2640) ===");

    // 1. Підключення до бездротової мережі
    connectToWiFi();

    // 2. Перевірка наявності зовнішньої оперативної пам'яті PSRAM
    if (psramFound()) {
        Serial.printf("Виявлено PSRAM. Загальний обсяг: %d байт, Вільний обсяг: %d байт\n",
                      ESP.getPsramSize(), ESP.getFreePsram());
    } else {
        Serial.println("УВАГА: Зовнішню PSRAM не виявлено! Робота буде обмежена стандартною DRAM.");
    }

    // 3. Ініціалізація модуля камери OV2640 (конфігурація AI-Thinker)
    CameraPins pins; // За замовчуванням розпіновка AI-Thinker ESP32-CAM
    esp_err_t err = camera.init(pins, FRAMESIZE_VGA, 12);
    if (err != ESP_OK) {
        Serial.printf("Критична помилка: Не вдалося ініціалізувати камеру (код 0x%x)\n", err);
        return;
    }

    // Налаштування орієнтації зображення для плати AI-Thinker
    camera.setFlip(false, true);

    // 4. Запуск MJPEG HTTP-відеосервера на порту 80
    err = streamer.start(80, camera);
    if (err != ESP_OK) {
        Serial.printf("Помилка запуску MJPEG-стримера (код 0x%x)\n", err);
        return;
    }

    Serial.println("=================================================");
    Serial.print("Відеопотік доступний за адресою: http://");
    Serial.print(WiFi.localIP());
    Serial.println("/stream");
    Serial.println("=================================================");
}

void loop() {
    // Періодичний моніторинг використання оперативної пам'яті PSRAM та Heap
    static unsigned long lastLogTime = 0;
    if (millis() - lastLogTime > 10000) {
        lastLogTime = millis();
        Serial.printf("[Монітор пам'яті] Вільна DRAM: %d байт | Вільна PSRAM: %d байт\n",
                      ESP.getFreeHeap(), ESP.getFreePsram());
    }

    delay(100);
}
