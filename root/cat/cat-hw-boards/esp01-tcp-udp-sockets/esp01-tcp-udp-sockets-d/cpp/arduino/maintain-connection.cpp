#include <ESP8266WiFi.h>

WiFiClient client;
unsigned long lastReconnectAttempt = 0;

void maintain_connection() {
    if (!client.connected()) {
        unsigned long now = millis();
        // Періодична спроба відновлення кожні 5 секунд
        if (now - lastReconnectAttempt > 5000) {
            lastReconnectAttempt = now;
            if (client.connect("192.168.1.100", 8080)) {
                // З'єднання успішно відновлено
            }
        }
    }
}
