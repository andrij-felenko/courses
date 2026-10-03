#include <Arduino.h>

// Ініціалізація мультиплексування та TCP-сервера через послідовний порт
bool setupMultiConnectionServer(uint16_t port) {
    // Включення режиму множинних з'єднань
    Serial.print(F("AT+CIPMUX=1\r\n"));
    if (!Serial.find("OK")) {
        Serial.println(F("// Помилка: не вдалося встановити AT+CIPMUX=1"));
        return false;
    }
    
    // Створення TCP-сервера на вказаному порту
    Serial.print(F("AT+CIPSERVER=1,"));
    Serial.print(port);
    Serial.print(F("\r\n"));
    
    if (Serial.find("OK")) {
        Serial.println(F("// TCP-сервер успішно запущено в режимі CIPMUX=1"));
        return true;
    }
    
    return false;
}
