#include <Arduino.h>

class ButtonDebouncer {
private:
    uint8_t _pin;
    uint8_t _history;
    bool _debouncedState;
    bool _lastStableState;

public:
    ButtonDebouncer(uint8_t pin) 
        : _pin(pin), _history(0xFF), _debouncedState(true), _lastStableState(true) {}

    void begin() {
        pinMode(_pin, INPUT_PULLUP);
    }

    // Викликається в регулярному інтервалі (наприклад, кожні 5 мс)
    bool update() {
        bool rawLevel = digitalRead(_pin);
        
        // Оновлюємо бітову маску історії
        _history = (_history << 1) | (rawLevel ? 1 : 0);

        if (_history == 0x00) {
            _debouncedState = false;
        } else if (_history == 0xFF) {
            _debouncedState = true;
        }

        bool pressedEvent = (_lastStableState && !_debouncedState);
        _lastStableState = _debouncedState;

        return pressedEvent;
    }

    bool isPressed() const {
        return !_debouncedState;
    }
};
