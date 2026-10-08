// C++ / Arduino: Безпечне перемикання двоканального мультиплексора на 74LVC1G125
#include <Arduino.h>

const uint8_t PIN_OE0 = 4;
const uint8_t PIN_OE1 = 5;

void selectChannel(uint8_t channel) {
    if (channel == 0) {
        // Вимикаємо вихід другого буфера (перехід у Hi-Z)
        digitalWrite(PIN_OE1, HIGH);
        delayMicroseconds(1); // Пауза для запобігання шинному конфлікту
        digitalWrite(PIN_OE0, LOW);
    } else {
        // Вимикаємо вихід першого буфера
        digitalWrite(PIN_OE0, HIGH);
        delayMicroseconds(1);
        digitalWrite(PIN_OE1, LOW);
    }
}
