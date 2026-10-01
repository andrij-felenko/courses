#include <ESP8266WiFi.h>
#include <ESP8266httpUpdate.h>

// Функція для автоматичного завантаження та встановлення прошивки по HTTPS
void processAutoUpdate(const char* serverUrl) {
    WiFiClientSecure client;
    // У виробничому коді слід задавати кореневий сертифікат CA
    client.setInsecure();

    // Запуск автоматичного циклу перевірки, завантаження та спалаху
    t_httpUpdate_return result = ESP8266httpUpdate.update(client, serverUrl);

    switch (result) {
        case HTTP_UPDATE_FAILED:
            // Отримання коду помилки та текстового опису
            break;
        case HTTP_UPDATE_NO_UPDATES:
            // Сервер повернув HTTP 304 - оновлення не потрібне
            break;
        case HTTP_UPDATE_OK:
            // Успішний запис, пристрій автоматично перезавантажується
            break;
    }
}
