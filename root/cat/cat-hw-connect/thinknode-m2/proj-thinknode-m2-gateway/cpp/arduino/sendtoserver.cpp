#include <WiFi.h>
#include <HTTPClient.h>

void sendToServer(uint8_t* payload, size_t length) {
    if (WiFi.status() != WL_CONNECTED) {
        return;
    }

    HTTPClient http;
    http.begin("http://api.myserver.com/data");
    http.addHeader("Content-Type", "application/octet-stream");

    http.POST(payload, length);
    http.end();
}
