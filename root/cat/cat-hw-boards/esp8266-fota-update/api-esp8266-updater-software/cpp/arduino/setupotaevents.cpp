#include <ESP8266httpUpdate.h>

void setupOTAEvents() {
    ESPhttpUpdate.onStart([]() {
        Serial.println("Початок завантаження оновлення...");
    });

    ESPhttpUpdate.onEnd([]() {
        Serial.println("\nЗавантаження завершено успішно!");
    });

    ESPhttpUpdate.onProgress([](int currentBytes, int totalBytes) {
        int percent = (currentBytes * 100) / totalBytes;
        Serial.printf("\rПрогрес оновлення: %d%% (%d / %d байт)", percent, currentBytes, totalBytes);
    });

    ESPhttpUpdate.onError([](int errorCode) {
        Serial.printf("\nПомилка OTA під час завантаження: код %d\n", errorCode);
    });
}
