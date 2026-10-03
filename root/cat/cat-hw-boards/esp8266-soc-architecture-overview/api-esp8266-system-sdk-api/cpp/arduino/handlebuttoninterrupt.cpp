// Приклад керування розміщенням коду у C++ (ESP8266 Arduino Core)
#include <Arduino.h>

// 1. Обробник переривання під час роботи в Arduino Core позначається IRAM_ATTR
void IRAM_ATTR handleButtonInterrupt() {
    // Швидкий код обробки у внутрішній оперативній пам'яті IRAM
    static unsigned long last_millis = 0;
    if (millis() - last_millis > 200) {
        last_millis = millis();
    }
}

// 2. Звичайна прикладна функція за замовчуванням розміщується у Flash
void processApplicationLogic() {
    Serial.println("Обробка прикладної логіки з Flash-пам'яті");
}
