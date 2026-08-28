#include <WiFi.h>

const char* SSID = "MyHome";
const char* PASS = "пароль";

void setup() {
    Serial.begin(115200);
    WiFi.mode(WIFI_STA);            // режим клієнта (station)
    WiFi.begin(SSID, PASS);         // скан + автентифікація + асоціація

    // чекаємо саме на IP: статус WL_CONNECTED настає з видачею адреси DHCP
    while (WiFi.status() != WL_CONNECTED) {
        delay(250);
        Serial.print('.');
    }
    Serial.print("\nIP: ");
    Serial.println(WiFi.localIP());   // напр. 192.168.1.12 — тепер ми в мережі
}
