#include <Arduino.h>

// Приклад неблокувального обходу опитування в C++
class ButtonHandler {
private:
    uint8_t pin;
    unsigned long lastCheck;
    const unsigned long intervalMs = 10;

public:
    ButtonHandler(uint8_t gpioPin) : pin(gpioPin), lastCheck(0) {}

    void begin() {
        pinMode(pin, INPUT_PULLUP);
    }

    // Замість нескінченного while(digitalRead(pin)) перевіряємо стан періодично
    void pollNonBlocking() {
        unsigned long now = millis();
        if (now - lastCheck >= intervalMs) {
            lastCheck = now;
            if (digitalRead(pin) == LOW) {
                onPress();
            }
        }
    }

    void onPress() {
        // Корисна обробка події без блокування процесорного ядра
    }
};
