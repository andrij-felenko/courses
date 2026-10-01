#include <ESP8266WiFi.h>

WiFiServer server(80);

void setup_tcp_server() {
    WiFi.begin("SSID", "PASSWORD");
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
    }
    server.begin();
}

void handle_tcp_clients() {
    WiFiClient client = server.available();
    if (client) {
        while (client.connected()) {
            if (client.available()) {
                String req = client.readStringUntil('\r');
                client.write("HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nOK");
                break;
            }
        }
        client.stop();
    }
}
