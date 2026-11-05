#include <Arduino.h>

constexpr uint8_t INPUT_PIN = 4;

class SchmittGpioInput {
private:
    uint8_t pin;

public:
    explicit SchmittGpioInput(uint8_t pinNumber) : pin(pinNumber) {}

    void begin() {
        // Конфігурація піна як вхід з внутрішнім pull-up підтягуванням.
        // Більшість MCU (AVR, ESP32, STM32) за замовчуванням задіюють вбудований тригер Шмітта.
        pinMode(pin, INPUT_PULLUP);
    }

    bool readState() const {
        // Зчитання цифрового стану, відфільтрованого вхідним тригером Шмітта
        return digitalRead(pin) == HIGH;
    }
};

SchmittGpioInput cleanInput(INPUT_PIN);

void setup() {
    Serial.begin(115200);
    cleanInput.begin();
}

void loop() {
    bool state = cleanInput.readState();
    // Використання відфільтрованого стану в логіці додатка
    delay(50);
}
