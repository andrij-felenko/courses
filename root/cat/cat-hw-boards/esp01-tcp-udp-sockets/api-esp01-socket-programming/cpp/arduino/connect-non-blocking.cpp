#include <ESP8266WiFi.h>

WiFiClient client;

void connect_non_blocking() {
    client.setNoDelay(true); // Вимкнення алгоритму Нагла для мінімізації затримок
    if (!client.connect("example.com", 80)) {
        // Обробка помилки підключення без зависання
        return;
    }
    client.print("GET / HTTP/1.1\r\nHost: example.com\r\n\r\n");
}

void poll_socket() {
    if (client.connected() && client.available()) {
        char c = client.read();
        // Обробка байта
    } else if (!client.connected()) {
        client.stop(); // Обов'язкове вивільнення ресурсів
    }
}
