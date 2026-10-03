// Приклад формування та відправки AT-команд у C++ (Arduino Framework)
#include <Arduino.h>

void setupAtDriver() {
    // Ініціалізація послідовного порту для обміну з ESP-AT модулем
    Serial1.begin(115200);
}

void demonstrateCommandTypes() {
    // 1. Тестова команда (Test): перевірка підтримуваних параметрів
    Serial1.print("AT+CWMODE=?\r\n");
    
    // 2. Опитувальна команда (Query): перевірка поточного режиму
    Serial1.print("AT+CWMODE?\r\n");
    
    // 3. Встановлювальна команда (Set): налаштування Wi-Fi підключення
    Serial1.print("AT+CWJAP=\"WiFi_Network\",\"Password123\"\r\n");
    
    // 4. Виконувана команда (Execute): запит версії прошивки
    Serial1.print("AT+GMR\r\n");
}
