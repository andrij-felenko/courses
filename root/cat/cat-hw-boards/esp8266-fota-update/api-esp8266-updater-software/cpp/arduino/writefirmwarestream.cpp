#include <ESP8266WiFi.h>
#include <Updater.h>

bool writeFirmwareStream(WiFiClient& client, size_t fileSize, const String& expectedMD5) {
    if (!Update.begin(fileSize, U_FLASH)) {
        Update.printError(Serial);
        return false;
    }

    if (expectedMD5.length() == 32) {
        Update.setMD5(expectedMD5.c_str());
    }

    uint8_t buffer[512];
    size_t writtenTotal = 0;

    while (client.connected() && writtenTotal < fileSize) {
        size_t availableBytes = client.available();
        if (availableBytes > 0) {
            size_t bytesToRead = min(availableBytes, sizeof(buffer));
            size_t bytesRead = client.read(buffer, bytesToRead);

            if (Update.write(buffer, bytesRead) != bytesRead) {
                Update.printError(Serial);
                return false;
            }
            writtenTotal += bytesRead;
        }
        yield(); // Запобігання спрацьовуванню Watchdog
    }

    if (!Update.end(true)) { // true підтверджує перевірку кінцевого розміру
        Update.printError(Serial);
        return false;
    }

    return true;
}
