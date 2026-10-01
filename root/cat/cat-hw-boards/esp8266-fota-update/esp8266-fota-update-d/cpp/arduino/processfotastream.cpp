#include <ESP8266WiFi.h>
#include <ESP8266httpUpdate.h>

bool processFotaStream(WiFiClient& client, uint32_t imageSize) {
    if (!Update.begin(imageSize)) {
        return false;
    }

    uint8_t buffer[512];
    uint32_t written = 0;

    while (written < imageSize && client.connected()) {
        size_t availableBytes = client.available();
        if (availableBytes > 0) {
            size_t bytesToRead = min(availableBytes, sizeof(buffer));
            size_t bytesRead = client.read(buffer, bytesToRead);

            if (Update.write(buffer, bytesRead) != bytesRead) {
                return false;
            }

            written += bytesRead;
            // Скидання сторожового таймера та обробка фонових задач Wi-Fi
            ESP.wdtFeed();
            yield();
        }
    }

    return Update.end(true);
}
