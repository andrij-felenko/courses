#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <ESP8266httpUpdate.h>

// SHA-1 відбиток SSL-сертифіката сервера оновлень
const char* serverFingerprint = "AA BB CC DD EE FF 01 02 03 04 05 06 07 08 09 10 11 12 13 14";

void checkForUpdates(const String& currentVersion) {
    WiFiClientSecure BearSSLClient;
    BearSSLClient.setFingerprint(serverFingerprint);

    t_httpUpdate_return ret = ESPhttpUpdate.update(BearSSLClient, "https://update.example.com/firmware.bin", currentVersion);

    switch (ret) {
        case HTTP_UPDATE_FAILED:
            Serial.printf("Помилка оновлення (%d): %s\n", 
                ESPhttpUpdate.getLastError(), 
                ESPhttpUpdate.getLastErrorString().c_str());
            break;
        case HTTP_UPDATE_NO_UPDATES:
            Serial.println("На сервері немає новішої версії");
            break;
        case HTTP_UPDATE_OK:
            Serial.println("Оновлення успішне, виконується перезапуск...");
            break;
    }
}
