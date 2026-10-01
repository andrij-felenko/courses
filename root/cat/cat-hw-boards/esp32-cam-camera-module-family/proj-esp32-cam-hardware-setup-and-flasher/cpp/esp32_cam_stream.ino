#include <WiFi.h>
#include "camera_config.hpp"

// Оголошення зовнішньої функції запуску веб-сервера
extern void start_video_server();

// Параметри Wi-Fi мережі
const char* ssid = "Your_SSID";
const char* password = "Your_PASSWORD";

CameraManager camera_mgr;

void setup() {
    Serial.begin(115200);
    Serial.setDebugOutput(true);
    Serial.println();

    // 1. Ініціалізація драйвера камери OV2640
    if (!camera_mgr.init()) {
        Serial.println("Помилка ініціалізації камери!");
        return;
    }
    Serial.println("Камеру успішно ініціалізовано.");

    // 2. Підключення до Wi-Fi
    WiFi.begin(ssid, password);
    Serial.print("Підключення до Wi-Fi");
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println();
    Serial.print("Wi-Fi підключено! IP-адреса: ");
    Serial.println(WiFi.localIP());

    // 3. Запуск веб-сервера відеостримінгу
    start_video_server();
    Serial.println("MJPEG відеопотік доступний за адресою: http://" + WiFi.localIP().toString() + "/stream");
}

void loop() {
    // Головний цикл вільний, веб-сервер обробляє запити асинхронно
    delay(10000);
}
