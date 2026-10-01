#include <ESP8266WiFi.h>

void send_telemetry_tcp(const char* host, uint16_t port, const uint8_t* payload, size_t len) {
    WiFiClient client;
    
    // Встановлення з'єднання з сервером
    if (!client.connect(host, port)) {
        return;
    }
    
    // Передавання даних у сокет
    client.write(payload, len);
    
    // Очікування відповіді з часовим обмеженням
    unsigned long start_time = millis();
    while (client.connected() && !client.available()) {
        if (millis() - start_time > 5000) {
            client.stop();
            return;
        }
        delay(10);
    }
    
    // Зчитування прибулих даних
    uint8_t rx_buffer[128];
    while (client.available() > 0) {
        int bytes_read = client.read(rx_buffer, sizeof(rx_buffer));
        if (bytes_read <= 0) break;
    }
    
    // Коректне закриття сокета
    client.stop();
}
