#include <ESP8266HTTPClient.h>
#include <WiFiClientSecure.h>

const int MAX_RETRY_ATTEMPTS = 5;
const unsigned long BASE_DELAY_MS = 1000;

bool downloadFirmwareWithBackoff(const char* url) {
    WiFiClientSecure client;
    client.setInsecure();
    
    HTTPClient http;
    
    for (int attempt = 0; attempt < MAX_RETRY_ATTEMPTS; attempt++) {
        if (http.begin(client, url)) {
            int httpCode = http.GET();
            if (httpCode == HTTP_CODE_OK) {
                Serial.println(F("[FOTA] З'єднання успішне"));
                http.end();
                return true;
            }
            http.end();
        }
        
        unsigned long delayMs = BASE_DELAY_MS << attempt;
        Serial.print(F("[FOTA] Помилка підключення, спроба "));
        Serial.print(attempt + 1);
        Serial.print(F(". Пауза "));
        Serial.print(delayMs);
        Serial.println(F(" мс"));
        
        delay(delayMs);
    }
    
    Serial.println(F("[FOTA] Помилка: вичерпано ліміт спроб"));
    return false;
}
