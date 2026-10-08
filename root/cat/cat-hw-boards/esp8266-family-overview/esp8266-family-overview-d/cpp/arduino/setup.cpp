// Ініціалізація автономного вузла та перехід у режим Deep Sleep
#include <ESP8266WiFi.h>

const char* ssid = "IoT_Network";
const char* password = "SecretPassword";

void setup() {
    Serial.begin(115200);
    
    // Активація бездротового модуля Wi-Fi
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(100);
    }
    
    // Після відправки даних переходимо в Deep Sleep на 10 хвилин (600 секунд)
    // Вивід GPIO16 повинен бути з'єднаний із виводом RST через діод Шотткі
    uint64_t sleepTimeUS = 600ULL * 1000000ULL;
    ESP.deepSleep(sleepTimeUS, WAKE_RF_DEFAULT);
}

void loop() {
    // Порожній цикл: після перезапуску з Deep Sleep виконання починається з setup()
}
