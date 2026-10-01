#include <ESP8266WiFi.h>
#include <ESP8266httpUpdate.h>

void perform_fota_update(const char* server_url) {
    WiFiClient client;
    t_httpUpdate_return ret = ESPhttpUpdate.update(client, server_url);

    switch (ret) {
        case HTTP_UPDATE_FAILED:
            Serial.printf("Помилка FOTA (%d): %s\n", 
                          ESPhttpUpdate.getLastError(), 
                          ESPhttpUpdate.getLastErrorString().c_str());
            break;
        case HTTP_UPDATE_NO_UPDATES:
            Serial.println("Оновлення відсутні");
            break;
        case HTTP_UPDATE_OK:
            Serial.println("Оновлення успішно виконано");
            break;
    }
}

void mark_app_valid(void) {
    ESP.otaUpdateConfirmed();
}
