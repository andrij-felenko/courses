#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <ESP8266httpUpdate.h>

// Функція перевірки та виконання оновлення по посиланню
void check_and_run_fota(const String& firmware_url) {
    WiFiClient client;
    
    // Налаштування обробників подій оновлення
    ESPhttpUpdate.onStart([]() { Serial.println("OTA: Старт запису Flash..."); });
    ESPhttpUpdate.onEnd([]() { Serial.println("OTA: Запис завершено успішно"); });
    ESPhttpUpdate.onError([](int err) { Serial.printf("OTA Помилка: %d\n", err); });

    // Виклик системного оновлення з переключенням банку
    t_httpUpdate_return result = ESPhttpUpdate.update(client, firmware_url);

    switch (result) {
        case HTTP_UPDATE_FAILED:
            Serial.printf("Помилка завантаження: (%d): %s\n", 
                          ESPhttpUpdate.getLastError(), 
                          ESPhttpUpdate.getLastErrorString().c_str());
            break;
        case HTTP_UPDATE_NO_UPDATES:
            Serial.println("Оновлення відсутні");
            break;
        case HTTP_UPDATE_OK:
            Serial.println("Оновлення виконано! Перезапуск...");
            break;
    }
}
