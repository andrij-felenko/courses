#include <ESP8266WiFi.h>

WiFiClient client;
unsigned long lastConnectAttempt = 0;

void handleNonBlockingConnection() {
    if (!client.connected()) {
        if (millis() - lastConnectAttempt > 5000) {
            lastConnectAttempt = millis();
            client.stop(); // Очищення попереднього сокета перед спробою
            client.setTimeout(1000); // Встановлення таймауту 1 сек
            if (client.connect("192.168.1.50", 80)) {
                client.setNoDelay(true);
            }
        }
    } else {
        while (client.available() > 0) {
            int c = client.read();
            // Обробка отриманого байта
        }
    }
}
