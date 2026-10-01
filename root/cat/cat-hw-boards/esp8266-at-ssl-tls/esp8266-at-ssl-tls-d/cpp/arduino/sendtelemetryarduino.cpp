#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClientSecure.h>

// C++ реалізація HTTPS POST-запиту для платформи Arduino ESP8266
void sendTelemetryArduino(const String& payload) {
    WiFiClientSecure client;
    client.setInsecure(); // Або client.setTrustAnchors(&certStore)
    HTTPClient https;
    if (https.begin(client, "https://api.example.com/api/v1/data")) {
        https.addHeader("Content-Type", "application/json");
        int httpCode = https.POST(payload);
        if (httpCode > 0) {
            Serial.printf("Код відповіді: %d\n", httpCode);
        }
        https.end();
    }
}
