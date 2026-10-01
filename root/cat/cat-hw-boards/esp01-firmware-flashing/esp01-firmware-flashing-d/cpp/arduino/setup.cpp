#include <ESP8266WiFi.h>

const char* ssid = "MyNetwork";
const char* password = "SecretPassword";

void setup() {
    Serial.begin(115200);
    delay(100);

    Serial.println();
    Serial.print("Flash chip real size: ");
    Serial.print(ESP.getFlashChipRealSize() / 1024);
    Serial.println(" KB");

    WiFi.begin(ssid, password);
    Serial.print("Connecting to Wi-Fi");

    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }

    Serial.println();
    Serial.print("Connected! IP address: ");
    Serial.println(WiFi.localIP());
}

void loop() {
    // Основний цикл програми
}
