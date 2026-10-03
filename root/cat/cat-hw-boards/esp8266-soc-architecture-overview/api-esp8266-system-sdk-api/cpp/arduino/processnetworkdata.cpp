// Приклад контролю динамічної пам'яті у C++ (ESP8266 Arduino Core)
#include <Arduino.h>

void processNetworkData(const uint8_t *data, size_t len) {
    // 1. Отримання доступного залишку Heap
    uint32_t freeHeap = ESP.getFreeHeap();
    Serial.printf("Поточний залишок Heap: %u байтів\n", freeHeap);

    if (freeHeap < 8192) {
        Serial.println("УВАГА: Критично низький рівень Heap!");
        return;
    }

    // 2. Виділення динамічного буфера
    uint8_t *buffer = new (std::nothrow) uint8_t[len];
    if (!buffer) {
        Serial.println("ПОМИЛКА: Не вдалося виділити пам'ять!");
        return;
    }

    // 3. Копіювання та обробка
    memcpy(buffer, data, len);

    // 4. Обов'язкове вилучення буфера
    delete[] buffer;
    buffer = nullptr;
}
